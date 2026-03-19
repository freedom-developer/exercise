#ifndef WSB_ASIO_BASIC_SOCKET_HPP
#define WSB_ASIO_BASIC_SOCKET_HPP

#include <type_traits>

#include <wsb/asio/executor.hpp>
#include <wsb/asio/execution_context.hpp>

namespace wsb {
namespace asio {

template <typename Protocol, typename Executor = executor>
class basic_socket
{
public:
    template <typename ExecutionContext>
    explicit basic_socket(ExecutionContext& context,
        typename std::enable_if<std::is_convertible<ExecutionContext&, execution_context&>::value>::type* = 0)
      : impl_(context)
    {
    }

protected:
    
};

}
}


#endif