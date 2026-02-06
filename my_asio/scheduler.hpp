#ifndef WSB_SCHEDULER_HPP
#define WSB_SCHEDULER_HPP

#include "posix_thread.hpp"
#include "scheduler_operation.hpp"
#include "op_queue.hpp"
#include "conditionally_enabled_mutex.hpp"
#include "scheduler_thread_info thread_info.hpp"

class scheduler
{
public:
    typedef scheduler_operation operation;
    typedef conditionally_enabled_mutex mutex;
    typedef scheduler_thread_info thread_info;
    inline scheduler();
    inline ~scheduler();

    inline size_t do_run_one(mutex::scoped_lock& lock, thread_info& this_thread, const error_code& ec);
private:
    struct task_operation : operation {
        task_operation() : operation(0) {}
    } task_operation_; // 一个调度器对象包含一个空操作
    op_queue<operation> op_queue_;
    posix_thread* thread_;
    bool stopped_;
    
};


#include "scheduler.ipp"

#endif