#ifndef WSB_ASIO_DETAIL_SERVICE_REGISTRY_HPP
#define WSB_ASIO_DETAIL_SERVICE_REGISTRY_HPP


namespace wsb {
namespace asio {

class io_context;

namespace detail {


class service_registry
{
public:
    template <typename Service>
    Service& use_service(io_context& ioc);
};

}
}
}


#endif