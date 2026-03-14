#ifndef WSB_ASIO_IMPL_IO_CONTEXT_HPP
#define WSB_ASIO_IMPL_IO_CONTEXT_HPP

#include <wsb/asio/detail/service_registry.hpp>

namespace wsb {
namespace asio {

// 针对 io_context 的 use_service 模板函数
// 此处 io_context 是完整类型，可以访问其成员
template <typename Service>
inline Service& use_service(io_context& ioc)
{
    // Check that Service meets the necessary type requirements.
    (void)static_cast<execution_context::service*>(static_cast<Service*>(0));
    (void)static_cast<const execution_context::id*>(&Service::id);
    return ioc.service_registry_->template use_service<Service>(ioc);
}

}
}

#endif
