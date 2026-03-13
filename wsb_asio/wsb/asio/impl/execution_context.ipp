#ifndef WSB_ASIO_IMPL_EXECUTION_CONTEXT_IPP
#define WSB_ASIO_IMPL_EXECUTION_CONTEXT_IPP

#include <wsb/asio/execution_context.hpp>

#include <wsb/asio/detail/service_registry.hpp>

namespace wsb {
namespace asio {

execution_context::execution_context() : service_registry_(new detail::service_registry(*this))
{
}

execution_context::~execution_context()
{
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

void execution_context::notify_fork(execution_context::fork_event ev)
{
    service_registry_->notify_fork(ev);
}



execution_context::service::service(execution_context& owner) : owner_(owner), next_(0) {}
execution_context::service::~service() {}

}
}

#endif