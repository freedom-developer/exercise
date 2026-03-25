#ifndef WSB_ASIO_IMPL_IO_CONTEXT_HPP
#define WSB_ASIO_IMPL_IO_CONTEXT_HPP

#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/io_context.hpp>

namespace wsb {
namespace asio {

template <typename Service>
Service& use_service(io_context& ioc)
{
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    (void)static_cast<const execution_context::id*>(&Service::id);

    return ioc.service_registry_->template use_service<Service>(ioc);
}

}
}

#endif