#ifndef WSB_ASIO_BASIC_SOCKET_ACCEPTOR_HPP
#define WSB_ASIO_BASIC_SOCKET_ACCEPTOR_HPP

#include <wsb/asio/socket_base.hpp>
#include <wsb/asio/execution_context.hpp>

namespace wsb {
namespace asio {

template <typename Protocol, typename Executor = execution_context>
class basic_socket_acceptor;

template <typename Protocol, typename Executor>
class basic_socket_acceptor : public socket_base {
public:

    typedef typename Protocol::endpoint endpoint_type;

    basic_socket_acceptor(const Executor& ex, const endpoint_type& endpoint, bool reuse_addr = true) : impl_(ex)
    {
        
    }

private:

};

}
}


#endif