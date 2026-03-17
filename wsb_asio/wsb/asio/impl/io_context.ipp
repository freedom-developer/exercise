#ifndef WSB_ASIO_IMPL_IO_CONTEXT_IPP
#define WSB_ASIO_IMPL_IO_CONTEXT_IPP

#include <wsb/asio/io_context.hpp>
#include <wsb/asio/detail/scoped_ptr.hpp>

namespace wsb {
namespace asio {

io_context::io_context() : impl_(add_impl(new detail::scheduler(*this, -1, false)))
{
}

io_context::~io_context()
{
}

std::size_t io_context::run()
{
    wsb::system::error_code ec;
    std::size_t s = impl_.run(ec);
    throw(ec);
    return 0;
}

detail::scheduler& io_context::add_impl(detail::scheduler* impl)
{
    detail::scoped_ptr<detail::scheduler> scoped_impl(impl);
    add_service<detail::scheduler>(*this, scoped_impl.get());
    return *scoped_impl.release();
}

}
}

#endif