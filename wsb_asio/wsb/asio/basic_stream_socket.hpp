#ifndef WSB_ASIO_BASIC_STREAM_HPP
#define WSB_ASIO_BASIC_STREAM_HPP

#include <type_traits>

#include <wsb/asio/executor.hpp>
#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/basic_socket.hpp>

namespace wsb {
namespace asio {

template <typename Protocol, typename Executor = executor>
class basic_stream_socket : public basic_socket
{
public:
    template <typename ExecutionContext>
    explicit basic_stream_socket(ExecutionContext& context, 
        typename std::enable_if<std::is_convertible<ExecutionContext&, execution_context&>::value>::type* = 0)
      : basic_socket<Protocol, Executor>(context)
    {
    }

};

}
}


#endif