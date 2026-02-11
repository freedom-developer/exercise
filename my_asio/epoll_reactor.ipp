#ifndef WSB_EPOLL_REACTOR_IPP
#define WSB_EPOLL_REACTOR_IPP

#include <sys/epoll.h>

#include "epoll_reactor.hpp"

namespace wsb {
namespace asio {

epoll_reactor::epoll_reactor(execution_context& ctx)
: execution_context_service_base<epoll_reactor>(ctx),
scheduler_(use_service<scheduler>(ctx)),
mutex_(scheduler_.concurrency_hint()),
interrupter_(),
epoll_fd_(do_epoll_create()),
timer_fd_(do_timerfd_create()),
shutdown_(false),
registered_descriptors_mutex_(mutex_.enabled())
{
    epoll_event ev = {0, { 0 }};
    ev.events = EPOLLIN | EPOLLOUT | EPOLLET;
    ev.data.ptr = &interrupter_;
    epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, interrupter_.read_descriptor(), &ev);
    interrupter_.interrupt(); // 触发interrupter_.read_descriptor()的一个读事件

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
    if (timer_fd_ != -1)
        close(timer_fd_);
}

void epoll_reactor::shutdown()
{
    conditionally_enabled_mutex::scoped_lock lock(mutex_);
    shutdown_ = true;
    lock.unlock();

    op_queue<scheduler_operation> ops;
    while (descriptor_state* state = registered_descriptors_.first()) {
        for (int i = 0; i < max_ops; ++i)
            ops.push(state->op_queue_[i]);
        state->shutdown_ = true;
        registered_descriptors_.free(state);
    }

    timer_queues_.get_all_timers(ops);
    scheduler_.abandon_operations(ops);
}

void epoll_reactor::notify_fork(execution_context::fork_event fork_ev)
{
    if (fork_ev == execution_context::fork_child) {
        if (epoll_fd_ != -1)
            ::close(epoll_fd_);
        epoll_fd_ = -1;
        epoll_fd_ = do_epoll_create();

        if (timer_fd_ != -1)
            ::close(timer_fd_);
        timer_fd_ = -1;
        timer_fd_ = do_timerfd_create();

        interrupter_.recreate();

        epoll_event ev = { 0, { 0 } };
        ev.events = EPOLLIN | EPOLLERR | EPOLLET;
        ev.data.ptr = &interrupter_;
        epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, interrupter_.read_descriptor(), &ev);
        interrupter_.interrupt();

        if (timer_fd_ != -1) {
            ev.events = EPOLLIN | EPOLLERR; 
            ev.data.ptr = &timer_fd_;
            epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, timer_fd_, &ev);
        }

        update_timeout();

        conditionally_enabled_mutex::scoped_lock descriptor_lock(registered_descriptors_mutex_);
        for (descriptor_state *state = registered_descriptors_.first(); state; state = state->next_) {
            ev.events = state->registered_events_;
            ev.data.ptr = state;
            int result = epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, state->descriptor_, &ev);
            if (result != 0) {
                error_code ec(errno);
                throw(ec);
            }
        }
    }
}

void epoll_reactor::init_task()
{
    scheduler_.init_task();
}

int epoll_reactor::register_descriptor(int descriptor, descriptor_data& data)
{
    data = allocate_descriptor_sate();

    {
        conditionally_enabled_mutex::scoped_lock lock(data->mutex_);
        data->reactor_ = this;
        data->descriptor_ = descriptor;
        data->shutdown_ = false;
        for (int i = 0; i < max_ops; ++i)
            data->try_speculative_[i] = true;
    }

    epoll_event ev = { 0, { 0 } };
    ev.events = EPOLLIN | EPOLLERR | EPOLLHUP | EPOLLPRI | EPOLLET;
    data->registered_events_ = ev.events;
    ev.data.ptr = data;
    int result = epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, descriptor, &ev);
    if (result != 0) {
        if (errno == EPERM) {
            data->registered_events_ = 0;
            return 0;
        }
        return errno;
    }

    return 0;
}

int epoll_reactor::register_internal_descriptor(int op_type, int descriptor, descriptor_data& data, reactor_op* op)
{
    data = allocate_descriptor_sate();

    {
        conditionally_enabled_mutex::scoped_lock lock(data->mutex_);
        data->reactor_ = this;
        data->descriptor_ = descriptor;
        data->shutdown_ = false;
        data->op_queue_[op_type].push(op);
        for (int i = 0; i < max_ops; ++i)
            data->try_speculative_[i] = true;
    }

    epoll_event ev = { 0, { 0 } };
    ev.events = EPOLLIN | EPOLLERR | EPOLLPRI | EPOLLHUP | EPOLLET;
    data->registered_events_ = ev.events;
    ev.data.ptr = data;
    int result = epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, descriptor, &ev);
    if (result != 0) {
        return errno;
    }

    return 0;
}

void epoll_reactor::move_descriptor(int descriptor, descriptor_data& target_data, descriptor_data& source_data)
{
    target_data = source_data;
    source_data = 0;
}

void epoll_reactor::start_op(int op_type, int descriptor, descriptor_data& data, reactor_op* op, bool is_continuation, bool allow_speculative)
{
    if (!data) {
        op->ec_ = EBADF;
        post_immediate_completion(op, is_continuation);
        return;
    }

    conditionally_enabled_mutex::scoped_lock lock(data->mutex_);
    if (data->shutdown_) {
        post_immediate_completion(op, is_continuation);
        return;
    }

    if (data->op_queue_[op_type].empty()) {
        if (allow_speculative && (op_type != read_op || data->op_queue_[except_op].empty())) {
            if (data->try_speculative_[op_type]) {
                if (reactor_op::status status = op->perform()) {
                    if (status == reactor_op::done_and_exhausted)
                        if (data->registered_events_ != 0)
                            data->try_speculative_[op_type] = false;
                    lock.unlock();
                    scheduler_.post_immediate_completion(op, is_continuation);
                    return;
                }
            }

            if (data->registered_events_ == 0) {
                op->ec_ = EOPNOTSUPP;
                scheduler_.post_immediate_completion(op, is_continuation);
                return;
            }

            if (op_type == write_op) {
                if ((data->registered_events_ & EPOLLOUT) == 0) {
                    epoll_event ev = {0, { 0 } };
                    ev.events = data->registered_events_ | EPOLLOUT;
                    ev.data.ptr = data;
                    if (epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, descriptor, &ev) == 0) {
                        data->registered_events_ |= ev.events;
                    } else {
                        op->ec_ = error_code(errno);
                        scheduler_.post_immediate_completion(op, is_continuation);
                        return;
                    }
                }
            }
        } else if (data->registered_events_ == 0) {
            op->ec_ = EOPNOTSUPP;
            scheduler_.post_immediate_completion(op, is_continuation);
            return;
        } else {
            if (op_type == write_op) {
                data->registered_events_ |= EPOLLOUT;
            }
            epoll_event ev = { 0, { 0 } };
            ev.events = data->registered_events_;
            ev.data.ptr = data;
            epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, descriptor, &ev);
        }
    }
    
    data->op_queue_[op_type].push(op);
    scheduler_.work_started();
}

void epoll_reactor::cancel_ops(int descriptor, descriptor_data& data)
{
    if (!data) return;
    conditionally_enabled_mutex::scoped_lock lock(data->mutex_);
    op_queue<scheduler_operation> ops;
    for (int i = 0; i < max_ops; ++i) {
        while (reactor_op* op = data->op_queue_[i].front()) {
            op->ec_ = ECANCELED;
            data->op_queue_[i].pop();
            ops.push(op);
        }
    }
    lock.unlock();
    scheduler_.post_deferred_completions(ops);
}

void epoll_reactor::deregister_descriptor(int descriptor, descriptor_data& data, bool closing)
{
    if (!data) return;
    conditionally_enabled_mutex::scoped_lock lock(data->mutex_);
    if (!data->shutdown_) {
        if (closing) {
            // 自动从epoll set中清除
        } else if (data->registered_events_ != 0) {
            epoll_event ev = { 0, { 0 } };
            epoll_ctl(epoll_fd_, EPOLL_CTL_DEL, descriptor, &ev);
        }

        op_queue<scheduler_operation> ops;
        for (int i = 0; i < max_ops; ++i) {
            while (reactor_op* op = data->op_queue_[i].front()) {
                op->ec_ = ECANCELED;
                data->op_queue_[i].pop();
                ops.push(op);
            }
        }

        data->descriptor_ = -1;
        data->shutdown_ = true;
        lock.unlock();
        scheduler_.post_deferred_completions(ops);
    } else {
        data = 0;
    }
}

void epoll_reactor::deregister_internal_descriptor(int descriptor, descriptor_data& data)
{
    if (!data) return;
    conditionally_enabled_mutex::scoped_lock lock(data->mutex_);
    if (!data->shutdown_) {

    } else {
        data = 0;
    }
}





epoll_reactor::descriptor_state::descriptor_state(bool locking)
: scheduler_operation(&epoll_reactor::descriptor_state::do_complete), mutex_(locking)
{
}

scheduler_operation* epoll_reactor::descriptor_state::perform_io(uint32_t events)
{
    mutex_.lock();
    perform_io_cleanup_on_block_exit io_cleanup(reactor_);
    conditionally_enabled_mutex::scoped_lock descriptor_lock(mutex_, conditionally_enabled_mutex::scoped_lock::adopt_lock);
    static const int flag[max_ops] = {EPOLLIN, EPOLLOUT, EPOLLPRI };
    for (int j = max_ops - 1; j >= 0; j--) {
        if (events & (flag[j] | EPOLLERR | EPOLLHUP)) {
            try_speculative_[j] = true;
            while (reactor_op* op = op_queue_[j].front())
            {
                if (reactor_op::status status = op->perform()) {
                    op_queue_[j].pop();
                    io_cleanup.ops_.push(op);
                    if (status == reactor_op::done_and_exhausted) {
                        try_speculative_[j] = false;
                        break;
                    }
                } else
                    break;
            }
        }
    }
    
    io_cleanup.first_op_ = io_cleanup.ops_.front();
    io_cleanup.ops_.pop();
    return io_cleanup.first_op_;
}

struct epoll_reactor::perform_io_cleanup_on_block_exit
{
    explicit perform_io_cleanup_on_block_exit(epoll_reactor* r): reactor_(r), first_op_(0) {}
    
    ~perform_io_cleanup_on_block_exit()
    {
        if (first_op_) {
            if (!ops_.empty())
                reactor_->scheduler_.post_defered_completions(ops_);
        } else {
            reactor_->scheduler_.compensating_work_started();
        }
    }

    epoll_reactor* reactor_;
    op_queue<scheduler_operation> ops_;
    scheduler_operation* first_op_;
};

void epoll_reactor::descriptor_state::do_complete(void* owner, scheduler_operation* base, const error_code& ec, std::size_t bytes_transfered)
{
    if (owner) {
        descriptor_state* descriptor_data = static_cast<descriptor_state*>(base);
        uint32_t events = static_cast<uint32_t>(bytes_transfered);
        if (scheduler_operation* op = descriptor_data->perform_io(events)) {
            op->complete(owner, ec, 0);
        }
    }
}

}
}

#endif