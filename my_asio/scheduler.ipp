

#ifndef WSB_SCHEDULER_IPP
#define WSB_SCHEDULER_IPP

#include "scheduler.hpp"

namespace wsb {
namespace asio {

size_t scheduler::do_run_one(conditionally_enabled_mutex::scoped_lock& lock, scheduler_thread_info& this_thread, const error_code& ec)
{
    while (!stopped_)
    {
        if (!op_queue_.empty()) {
            scheduler_operation* o = op_queue_.front();
            op_queue_.pop();
            bool more_handlers = (!op_queue_.empty());
            if (o == &task_operation_) {
                task_interrupted_ = more_handlers;
                if (more_handlers && !one_thread_)
                    wakeup_event_.unlock_and_signal_one(lock);
            } else {

            }
        }
    }
    
    return 0;
}

} // asio
} // namespace wsb

#endif