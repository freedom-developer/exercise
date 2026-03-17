#ifndef WSB_ASIO_BASIC_SOCKET_ACCEPTOR_HPP
#define WSB_ASIO_BASIC_SOCKET_ACCEPTOR_HPP

#include <wsb/asio/socket_base.hpp>
#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/io_object_impl.hpp>

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
        wsb::system::error_code ec;
        impl_.get_service().open(impl_.get_implementation(), protocol, ec);
        throw(ec);
    }

private:
    detail::io_object_impl<detail::reactive_socket_service<Protocol>, Executor> impl_;
};

}
}


#endif