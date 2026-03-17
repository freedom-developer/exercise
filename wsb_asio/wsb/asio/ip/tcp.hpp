#ifndef WSB_ASIO_IP_TCP_HPP
#define WSB_ASIO_IP_TCP_HPP

#include <wsb/asio/ip/basic_endpoint.hpp>
#include <wsb/asio/basic_socket_acceptor.hpp>

#include <sys/types.h>
#include <sys/socket.h>

namespace wsb {
namespace asio {
namespace ip {

class tcp {
public:
    typedef basic_endpoint<tcp> endpoint;
    typedef basic_socket_acceptor<tcp> acceptor;

    static tcp v4() noexcept
    { return tcp(AF_INET); }

private:
    explicit tcp(int family) : family_(family) {}

    int family_;
};

}
}
}

#endif