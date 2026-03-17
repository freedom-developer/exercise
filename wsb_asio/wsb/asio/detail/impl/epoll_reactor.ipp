#ifndef WSB_ASIO_DETAIL_EPOLL_REACTOR_IPP
#define WSB_ASIO_DETAIL_EPOLL_REACTOR_IPP

#include <wsb/asio/detail/epoll_reactor.hpp>
#include <wsb/system/error_code.hpp>

#include <sys/epoll.h>
#include <sys/timerfd.h>

namespace wsb {
namespace asio {
namespace detail {

epoll_reactor::epoll_reactor(wsb::asio::execution_context& ctx)
: execution_context_service_base<epoll_reactor>(ctx),
scheduler_(use_service<scheduler>(ctx)),
mutex_(true),
interrupter_(),
epoll_fd_(do_epoll_create()),
timer_fd_(do_timerfd_create()),
shutdown_(false),
registered_descriptors_mutex_(mutex_.enabled())
{
    // 将interrupter_.read_descriptor()添加到epfd
    epoll_event ev = { 0, { 0 } };
    ev.events = EPOLLIN | EPOLLERR | EPOLLET;
    ev.data.ptr = &interrupter_;
    epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, interrupter_.read_descriptor(), &ev);
    interrupter_.interrupt(); // 向interrupt_.write_descriptor()中写入一个1

    // 将timerfd添加到epfd
    if (timer_fd_ != -1) {
        ev.events = EPOLLIN | EPOLLERR; 
        ev.data.ptr = &timer_fd_;
        epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, timer_fd_, &ev);
    }
}

epoll_reactor::~epoll_reactor()
{
    if (epoll_fd_ != -1)
        close(epoll_fd_);
    if (timer_fd_)
        close(epoll_fd_);
}

int epoll_reactor::do_epoll_create()
{
#ifdef EPOLL_CLOEXEC
    int fd = epoll_create1(EPOLL_CLOEXEC);
#else
    fd = -1;
    errno = EINVAL;
#endif
    if (fd == -1 && (errno == EINVAL || ENOSYS)) {
        fd = epoll_create(epoll_size);
        if (fd != -1)
            ::fcntl(fd, F_SETFD, FD_CLOEXEC);
    }

    if (fd == -1) {
        wsb::system::error_code ec(errno, wsb::system::system_category());
        throw(ec);
    }

    return fd;
}

int epoll_reactor::do_timerfd_create()
{
    int fd = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    if (fd == -1 && errno == EINVAL) {
        fd = timerfd_create(CLOCK_MONOTONIC, 0);
        if (fd != -1)
            ::fcntl(fd, F_SETFD, FD_CLOEXEC);
    }
    return fd;
}

epoll_reactor::per_descriptor_data epoll_reactor::allocate_descriptor_state()
{
  conditionally_enabled_mutex::scoped_lock descriptors_lock(registered_descriptors_mutex_);
  return registered_descriptors_.alloc(true);
}

void epoll_reactor::interrupt()
{
    epoll_event ev = { 0, { 0 } };
    ev.events = EPOLLIN | EPOLLERR | EPOLLET;
    ev.data.ptr = &interrupter_;
    epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, interrupter_.read_descriptor(), &ev);
}

struct epoll_reactor::perform_io_cleanup_on_block_exit {
    explicit perform_io_cleanup_on_block_exit(epoll_reactor* r) : reactor_(r), first_op_(0) {}
    ~perform_io_cleanup_on_block_exit()
    {
        if (first_op_) {
            if (!ops_.empty())
                reactor_->scheduler_.post_deferred_completions(ops_);
        } else {
            reactor_->scheduler_.compensating_work_started();
        }
    }

    epoll_reactor* reactor_;
    op_queue<scheduler_operation> ops_;
    scheduler_operation* first_op_;
};

scheduler_operation* epoll_reactor::descriptor_state::perform_io(uint32_t events)
{
    mutex_.lock();
    perform_io_cleanup_on_block_exit io_cleanup(reactor_);
    conditionally_enabled_mutex::scoped_lock lock(mutex_, conditionally_enabled_mutex::scoped_lock::adopt_lock); // 已经锁了的，使用这种方式管理
    
    static const int flag[max_ops] = { EPOLLIN, EPOLLOUT, EPOLLPRI };
    
    for (int j = max_ops - 1; j >= 0; --j) {
        if (events & flag[j] | EPOLLERR | EPOLLHUP) {
            try_speculative_[j] = true; // 对应的项有事件发生
            while (reactor_op *op = op_queue_[j].front()) {
                if (reactor_op::status status = op->perform()) {
                    op_queue_[j].pop();
                    io_cleanup.ops_.push(op);
                    if (status == reactor_op::done_and_exhausted) {
                        try_speculative_[j] = false; 
                        break;
                    }
                } else break;
            }
        }
    }

    io_cleanup.first_op_ = io_cleanup.ops_.front();
    io_cleanup.ops_.pop();
    return io_cleanup.first_op_;
}

void epoll_reactor::descriptor_state::do_complete(void *owner, scheduler_operation* base, const wsb::system::error_code& ec, std::size_t bytes_transferred)
{
    if (owner) {
        descriptor_state* descriptor_data = static_cast<descriptor_state*>(base);
        uint32_t events = static_cast<uint32_t>(bytes_transferred);
        if (scheduler_operation* op = descriptor_data->perform_io(events))
            op->complete(owner, ec, 0);
    }
}

epoll_reactor::descriptor_state::descriptor_state(bool locking) : 
scheduler_operation(&epoll_reactor::descriptor_state::do_complete), mutex_(locking) {}

}
}
}


#endif