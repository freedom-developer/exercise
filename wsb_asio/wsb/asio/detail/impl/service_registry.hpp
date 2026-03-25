#ifndef WSB_ASIO_DETAIL_IMPL_SERVICE_REGISTRY_HPP
#define WSB_ASIO_DETAIL_IMPL_SERVICE_REGISTRY_HPP

#include <wsb/asio/detail/service_registry.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename Service>
Service& service_registry::use_service(io_context& owner)
{
  execution_context::service::key key;
  init_key<Service>(key, 0);
  factory_type factory = &service_registry::create<Service, io_context>;
  return *static_cast<Service*>(do_use_service(key, factory, &owner));
}

}
}
}


#endif