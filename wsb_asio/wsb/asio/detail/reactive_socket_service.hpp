#ifndef WSB_ASIO_DETAIL_REACTIVE_SOCKET_SERVICE_HPP
#define WSB_ASIO_DETAIL_REACTIVE_SOCKET_SERVICE_HPP

#include <wsb/asio/execution_context.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename Protocol>
class reactive_socket_service : public execution_context_service_base<reactive_socket_service<Protocol>>, public reactive_socket_service_base {
public:
    
private:

};

}
}
}


#endif
