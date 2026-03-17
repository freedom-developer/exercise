#ifndef WSB_ASIO_IP_BASIC_ENDPOINT_HPP
#define WSB_ASIO_IP_BASIC_ENDPOINT_HPP

#include <wsb/asio/ip/detail/endpoing.hpp>

namespace wsb {
namespace asio {
namespace ip {

template <typename InternetProtocol>
class basic_endpoint {
public:
    basic_endpoint(const InternetProtocol& protocol, unsigned short port) noexcept
    : impl_(protocol.family(), port) {}

private:
    detail::endpoint impl_;
};

}
}
}


#endif