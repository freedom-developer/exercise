#ifndef WSB_ASIO_DETAIL_SCHEDULER_IPP
#define WSB_ASIO_DETAIL_SCHEDULER_IPP

#include <wsb/asio/detail/scheduler.hpp>
#include <wsb/asio/detail/scheduler_thread_info.hpp>

namespace wsb {
namespace asio {
namespace detail {

scheduler::scheduler(execution_context& ctx, int concurrency_hint, bool own_thread) 
: wsb::asio::execution_context_service_base<scheduler>(ctx),
one_thread_(true),
mutex_(false),
stopped_(false),
task_(0),
task_interrupted_(true),
outstanding_work_(0)
{

}

void scheduler::shutdown()
{
    
}

void scheduler::post_deferred_completions(op_queue<scheduler_operation>& ops)
{

}

void scheduler::compensating_work_started()
{
    
}

std::size_t scheduler::run(wsb::system::error_code& ec)
{
    ec = wsb::system::error_code();
    if (outstanding_work_ == 0) {
        stop();
        return 0;
    }

    scheduler_thread_info this_thread;
    this_thread.private_outstanding_work = 0;
    thread_call_stack::context ctx(this, this_thread);

    conditionally_enabled_mutex::scoped_lock lock(mutex_);

    std::size_t n = 0;
    // for (; do_run_one(lock, this_thread, ec); lock.lock())
    //     if (n != (std::numeric_limits<std::size_t>::max)())
    //         n++;
    return n;
}

void scheduler::stop()
{
    conditionally_enabled_mutex::scoped_lock lock(mutex_);
    stop_all_threads(lock);
}

void scheduler::stop_all_threads(conditionally_enabled_mutex::scoped_lock& lock)
{
    stopped_ = true;
    wakeup_event_.signal_all(lock);
    if (!task_interrupted_ && task_) {
        task_interrupted_ = true;
        task_->interrupt();
    }
}

}
}
}

#endif