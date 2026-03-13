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

template <typename Service>
Service& service_registry::use_service()
{
    execution_context::service::key key;
    init_key<Service>(key, 0);
    factory_type factory = &service_registry::create<Service, execution_context>;
    return *static_cast<Service*>(do_use_service(key, factory, &owner_));
}

template <typename Service>
Service& service_registry::use_service(io_context& owner)
{
    execution_context::service::key key;
    init_key<Service>(key, 0);
    factory_type factory = &service_registry::create<Service, io_context>;
    return *static_cast<Service*>(do_use_service(key, factory, &owner));
}

template <typename Service>
void service_registry::add_service(Service* new_service)
{
    execution_context::service::key key;
    init_key<Service>(key, 0);
    return do_add_service(key, new_service);
}

template <typename Service>
bool service_registry::has_service() const
{
  execution_context::service::key key;
  init_key<Service>(key, 0);
  return do_has_service(key);
}



}
}
}


#endif