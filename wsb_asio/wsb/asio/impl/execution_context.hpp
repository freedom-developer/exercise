#ifndef WSB_ASIO_IMPL_EXECUTION_CONTEXT_HPP
#define WSB_ASIO_IMPL_EXECUTION_CONTEXT_HPP

#include <wsb/asio/detail/service_registry.hpp>

namespace wsb {
namespace asio {


inline execution_context& execution_context::service::context()
{
    return owner_;
}

}
}

#endif