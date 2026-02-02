#ifndef WSB_SCHEDULER_HPP
#define WSB_SCHEDULER_HPP

#include "posix_thread.hpp"
#include "scheduler_operation.hpp"
#include "op_queue.hpp"

class scheduler
{
public:
    typedef scheduler_operation operation;
    inline scheduler();
    inline ~scheduler();
private:
    struct task_operation : operation {
        task_operation() : operation(0) {}
    } task_operation_; // 一个调度器对象包含一个空操作
    op_queue<operation> op_queue_;
    posix_thread* thread_;
};


#include "scheduler.ipp"

#endif