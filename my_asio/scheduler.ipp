

#ifndef WSB_SCHEDULER_IPP
#define WSB_SCHEDULER_IPP

#include "scheduler.hpp"

namespace wsb {
namespace asio {

struct scheduler::task_cleanup
{
    ~task_cleanup()
    {
        if (this_thread_->private_outstanding_work > 0) {
            std::atomic_fetch_add(&scheduler_->outstanding_work_, this_thread_->private_outstanding_work);
        }
        this_thread_->private_outstanding_work = 0;
        lock_->lock();
        scheduler_->task_interrupted_ = true;
        scheduler_->op_queue_.push(this_thread_->private_op_queue);
        scheduler_->op_queue_.push(&scheduler_->task_operation_);
    }

    scheduler* scheduler_;
    conditionally_enabled_mutex::scoped_lock* lock_;
    scheduler_thread_info* this_thread_;
};

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
                else
                    lock.unlock();
                
                task_cleanup on_exit = { this, &lock, &this_thread };
                (void)on_exit;

                task_->run(more_handlers ? 0 : -1, this_thread.private_op_queue);
            } else {

            }
        }
    }
    
    return 0;
}

} // asio
} // namespace wsb

#endif