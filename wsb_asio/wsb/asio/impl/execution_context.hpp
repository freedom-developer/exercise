#ifndef WSB_ASIO_IMPL_EXECUTION_CONTEXT_HPP
#define WSB_ASIO_IMPL_EXECUTION_CONTEXT_HPP

#include <wsb/asio/detail/service_registry.hpp>
#include <wsb/asio/detail/scoped_ptr.hpp>

namespace wsb {
namespace asio {


inline execution_context& execution_context::service::context()
{
    return owner_;
}

template <typename Service>
inline Service& use_service(execution_context& e)
{
    // Check that Service meets the necessary type requirements.
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    return e.service_registry_->template use_service<Service>();
}

template <typename Service>
inline Service& use_service(io_context& ioc)
{
    // Check that Service meets the necessary type requirements.
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    (void)static_cast<const execution_context::id*>(&Service::id);
    return ioc.service_registry_->template use_service<Service>(ioc);
}

template <typename Service, typename... Args>
Service& make_service(execution_context& e, Args&&... args)
{
    detail::scoped_ptr ptr(new Service(e, static_cast<Args&&>(args)...));
    e.service_registry_->template add_service<Service>(ptr.get());
    Service& result = *ptr;
    ptr.release();
    return result;
}

template <typename Service>
void add_service(execution_context& e, Service* svc)
{
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    e.service_registry_->template add_service<Service>(svc);
}

template <typename Service>
bool has_service(execution_context& e)
{
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    return e.service_registry_->template has_service<Service>();
}

}
}

#endif