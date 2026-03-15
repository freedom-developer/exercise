#ifndef WSB_ASIO_DETAIL_EPOLL_REACTOR_IPP
#define WSB_ASIO_DETAIL_EPOLL_REACTOR_IPP

#include <wsb/asio/detail/epoll_reactor.hpp>
#include <wsb/system/error_code.hpp>

#include <sys/epoll.h>

namespace wsb {
namespace asio {
namespace detail {

epoll_reactor::epoll_reactor(wsb::asio::execution_context& ctx)
: execution_context_service_base<epoll_reactor>(ctx),
mutex_(true),
scheduler_(use_service<scheduler>(ctx)),
epoll_fd_(do_epoll_create())
{

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