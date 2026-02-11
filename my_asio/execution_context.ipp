#ifndef WSB_EXECUTION_CONTEXT_IPP
#define WSB_EXECUTION_CONTEXT_IPP

#include "execution_context.hpp"
#include "service_registry.hpp"

namespace wsb {
namespace asio {

template <typename Service>
bool has_service(execution_context&  e)
{
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    return e.service_registry_->template has_service<Service>();
}

template <typename Service>
void add_service(execution_context& e, Service* svc)
{
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    e.service_registry_->template add_service<Service>(svc);
}

template <typename Service>
Service& use_service(execution_context& e)
{
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    return e.service_registry_->template use_service<Service>();
}

void execution_context::notify_fork(fork_event event)
{
    service_registry_->notify_fork(event);
}

execution_context::execution_context(): service_registry_(new service_registry(*this))
{
}

execution_context::~execution_context()
{
    shutdown();
    destroy();
    delete service_registry_;
}

void execution_context::shutdown()
{
    service_registry_->shutdown_services();
}

void execution_context::destroy()
{
    service_registry_->destroy_services();
}

}
}

#endif