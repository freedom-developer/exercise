#ifndef WSB_ASIO_IP_DETAIL_ENDPOINT_HPP
#define WSB_ASIO_IP_DETAIL_ENDPOINT_HPP

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <cstddef>

#include <wsb/system/error_code.hpp>

namespace wsb {
namespace asio {
namespace ip {
namespace detail {

class endpoint {
public:
    inline endpoint(int family, unsigned short port) noexcept
    {
        if (family == AF_INET) {
            data_.v4.sin_family = AF_INET;
            data_.v4.sin_port = ::htons(port);
            data_.v4.sin_addr.s_addr = ::htonl(INADDR_ANY);
        } else {
            memset(&data_.v6, 0, sizeof(sockaddr_in6));
            data_.v6.sin6_family = AF_INET6;
            data_.v6.sin6_port = ::htons(port);
        }
    }

private:
    union data_union
    {
        sockaddr base;
        sockaddr_in v4;
        sockaddr_in6 v6;
    } data_;
    
};

}
}
}
}


#endif