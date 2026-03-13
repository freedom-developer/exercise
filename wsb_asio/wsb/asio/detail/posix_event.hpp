#ifndef WSB_ASIO_DETAIL_POSIX_EVENT_HPP
#define WSB_ASIO_DETAIL_POSIX_EVENT_HPP

#include <wsb/asio/detail/noncopyable.hpp>

#include <pthread.h>
#include <cstddef>

namespace wsb {
namespace asio {
namespace detail {

class posix_event : private noncopyable {
public:

private:
    ::pthread_cond_t cond_;
    std::size_t state_;
};

}
}
}


#endif