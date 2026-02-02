#ifndef WSB_SCHEDULER_OPERATION_HPP
#define WSB_SCHEDULER_OPERATION_HPP

#include "error_code.hpp"

// 调度操作对象 就是一个 回调函数
class scheduler_operation
{
public:
    void complete(void *owner, const error_code& ec, size_t bytes_transfered)
    { // 调用回调函数func_
        func_(owner, this, ec, bytes_transfered);
    }
    void destroy()
    {
        func_(0, this, error_code(), 0);
    }

protected:
    typedef void (*func_type)(void *, scheduler_operation*, const error_code&, size_t);
    unsigned int task_result_;

    scheduler_operation(func_type func): next_(0), func_(func), task_result_(0) {}
    ~scheduler_operation() {}

private:
    scheduler_operation* next_;
    func_type func_;
};


#endif