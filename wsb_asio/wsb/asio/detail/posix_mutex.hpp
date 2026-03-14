#ifndef WSB_ASIO_DETAIL_POSIX_MUTEX_HPP
#define WSB_ASIO_DETAIL_POSIX_MUTEX_HPP

#include <wsb/asio/detail/noncopyable.hpp>
#include <pthread.h>
#include <wsb/system/error_code.hpp>
#include <wsb/asio/detail/scoped_lock.hpp>

namespace wsb {
namespace asio {
namespace detail {

class conditionally_enabled_event;

class posix_mutex : private noncopyable {
public:
    typedef wsb::asio::detail::scoped_lock<posix_mutex> scoped_lock;
    inline posix_mutex() 
    {
        int error = ::pthread_mutex_init(&mutex_, 0);
        if (error) {
            wsb::system::error_code ec(error, wsb::system::system_category());
            throw(ec);
        }
    }

    inline ~posix_mutex()
    {
        ::pthread_mutex_destroy(&mutex_);
    }

    void lock() { ::pthread_mutex_lock(&mutex_); }
    void unlock() { ::pthread_mutex_unlock(&mutex_); }

private:
    friend class posix_event;

    ::pthread_mutex_t mutex_;
};

}
}
}


#endif