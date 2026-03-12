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



execution_context::service::service(execution_context& owner) : owner_(owner), next_(0) {}
execution_context::service::~service() {}
void execution_context::service::notify_fork(execution_context::fork_event) {}

}
}

#endif