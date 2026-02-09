#ifndef REACTOR_OP_HPP
#define REACTOR_OP_HPP

#include "scheduler_operation.hpp"
#include "error_code.hpp"

namespace wsb {
namespace asio {

class reactor_op : public scheduler_operation
{
public:
    error_code ec_;
    std::size_t bytes_transfered_;
    enum status { not_done, done, done_and_exhausted };
    status perform()
    {
        return perform_func_(this);
    }
protected:
    typedef status (*perform_func_type)(reactor_op*);
    reactor_op(const error_code& success_ec, perform_func_type perform_func, func_type complete_func)
    : scheduler_operation(complete_func), ec_(success_ec), bytes_transfered_(0), perform_func_(perform_func) {}
private:
    perform_func_type perform_func_;
};

}
}

#endif