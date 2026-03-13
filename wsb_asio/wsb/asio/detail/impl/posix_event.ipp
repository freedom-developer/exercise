#ifndef WSB_ASIO_DETAIL_IMPL_POSIX_EVENT_IPP
#define WSB_ASIO_DETAIL_IMPL_POSIX_EVENT_IPP

#include <wsb/asio/detail/posix_event.hpp>
#include <wsb/system/error_code.hpp>
#include <exception>

namespace wsb {
namespace asio {
namespace detail {

posix_event::posix_event() : state_(0) 
{
    ::pthread_condattr_t attr;
    ::pthread_condattr_init(&attr);
    int error = ::pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
    if (error == 0)
        error = ::pthread_cond_init(&cond_, &attr);
    if (error) {
        wsb::system::error_code ec(error, wsb::system::system_category());
        throw(ec);
    }
}

}
}
}


#endif