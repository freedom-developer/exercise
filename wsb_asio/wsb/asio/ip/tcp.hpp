#ifndef WSB_ASIO_TCP_HPP
#define WSB_ASIO_TCP_HPP

#include <wsb/asio/basic_stream_socket.hpp>

namespace wsb {
namespace asio {
namespace ip {


class tcp
{
public:
    typedef wsb::asio::basic_stream_socket<tcp> socket;

};

}
}
}




#endif