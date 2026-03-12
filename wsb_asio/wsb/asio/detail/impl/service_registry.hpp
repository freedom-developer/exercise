#ifndef WSB_ASIO_DETAIL_IMPL_SERVICE_REGISTRY_HPP
#define WSB_ASIO_DETAIL_IMPL_SERVICE_REGISTRY_HPP

#include <wsb/asio/detail/service_registry.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename Service>
inline void service_registry::init_key(execution_context::service::key& key, ...)
{
    init_key_from_id(key, Service::id);
}

template <typename Service, typename Owner>
execution_context::service* service_registry::create(void *owner)
{
    return new Service(*static_cast<Owner*>(owner));
}

}
}
}


#endif