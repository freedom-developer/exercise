#ifndef WSB_ASIO_DETAIL_POSIX_EVENT_HPP
#define WSB_ASIO_DETAIL_POSIX_EVENT_HPP

#include <wsb/asio/detail/noncopyable.hpp>

#include <pthread.h>
#include <cstddef>
#include <cassert>

namespace wsb {
namespace asio {
namespace detail {

class posix_event : private noncopyable {
public:
    inline posix_event();
    ~posix_event() { ::pthread_cond_destroy(&cond_); }

    template <typename Lock>
    void signal(Lock& lock) { this->signal_all(lock); }

    template <typename Lock>
    void signal_all(Lock& lock)
    {
        assert(lock.locked());
        (void)lock;
        state_ |= 1;
        ::pthread_cond_broadcast(&cond_);
    }

    template <typename Lock>
    void unlock_and_signal_one(Lock& lock)
    {
        
    }

private:
    ::pthread_cond_t cond_;
    std::size_t state_;
};

}
}
}

#include <wsb/asio/detail/impl/posix_event.ipp>

#endif