#ifndef WSB_ASIO_DETAIL_HTREAD_CONTEXT_HPP
#define WSB_ASIO_DETAIL_HTREAD_CONTEXT_HPP

#include <wsb/asio/detail/call_stack.hpp>

namespace wsb {
namespace asio {
namespace detail {

class thread_info_base;

class thread_context {
public:
    typedef call_stack<thread_context, thread_info_base> thread_call_stack;
};

}
}
}



#endif