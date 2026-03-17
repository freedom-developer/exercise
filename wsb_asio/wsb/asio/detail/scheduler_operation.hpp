#ifndef WSB_ASIO_DETAIL_SCHEDULER_OPERATION_HPP
#define WSB_ASIO_DETAIL_SCHEDULER_OPERATION_HPP

#include <wsb/system/error_code.hpp>

namespace wsb {
namespace asio {
namespace detail {

class scheduler_operation {
public:
    void complete(void* owner, const wsb::system::error_code& ec, std::size_t bytes_transferred)
    {
        func_(owner, this, ec, bytes_transferred);
    }

    void destroy()
    {
        func_(0, this, wsb::system::error_code(), 0);
    }

protected:
    typedef void (*func_type)(void*, scheduler_operation*, const wsb::system::error_code&, std::size_t);
    scheduler_operation(func_type func): next_(0), func_(func), task_result_(0) {}
    ~scheduler_operation() {}

private:
    friend class op_queue_access;
    scheduler_operation* next_;
    func_type func_;

protected:
    friend class scheduler;
    unsigned int task_result_;
};

}
}
}


#endif
