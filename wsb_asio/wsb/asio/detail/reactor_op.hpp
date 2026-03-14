#ifndef WSB_ASIO_DETAIL_REACTOR_OP_HPP
#define WSB_ASIO_DETAIL_REACTOR_OP_HPP

#include <wsb/asio/detail/scheduler_operation.hpp>

namespace wsb {
namespace asio {
namespace detail {

class reactor_op : public scheduler_operation {
public:
    wsb::system::error_code ec_;
    std::size_t bytes_transferred_;
    enum status { not_done, done, done_and_exhausted };

    status perform() { return perform_func_(this); }

protected:
    typedef status (*perform_func_type)(reactor_op*);
    
    reactor_op(const wsb::system::error_code& ec, perform_func_type func, func_type complete_func) : 
    scheduler_operation(complete_func), ec_(ec), bytes_transferred_(0), perform_func_(func) 
    {}

private:
    perform_func_type perform_func_;
};

}
}
}

#endif