#ifndef WSB_SCHEDULER_HPP
#define WSB_SCHEDULER_HPP

#include "posix_thread.hpp"
#include "scheduler_operation.hpp"
#include "op_queue.hpp"
#include "conditionally_enabled_mutex.hpp"
#include "thread_info_base.hpp"

namespace wsb {
namespace asio {

class scheduler
{
public:
    inline scheduler(): thread_(0), one_thread_(false) {}
    inline ~scheduler() {}

    inline size_t do_run_one(conditionally_enabled_mutex::scoped_lock& lock, scheduler_thread_info& this_thread, const error_code& ec);

private:
    const bool one_thread_;
    struct task_operation : scheduler_operation {
        task_operation() : scheduler_operation(0) {}
    } task_operation_; // 一个调度器对象包含一个空操作
    bool task_interrupted_;
    op_queue<scheduler_operation> op_queue_;
    posix_thread* thread_;
    bool stopped_;

};

} // asio
} // wsb


#include "scheduler.ipp"

#endif