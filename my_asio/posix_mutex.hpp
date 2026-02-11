#ifndef WSB_POSIX_MUTEX_HPP
#define WSB_POSIX_MUTEX_HPP

#include <pthread.h>

#include "error_code.hpp"
#include "noncopyable.hpp"

namespace wsb {
namespace asio {

class posix_mutex : private noncopyable
{
public:
    inline posix_mutex()
    {
        int error = ::pthread_mutex_init(&mutex_, 0);
        if (error != 0) {
            error_code ec(error, system_category());
            throw(ec);
        }
    }
    ~posix_mutex()
    {
        ::pthread_mutex_destroy(&mutex_);
    }
    void lock()
    {
        (void)::pthread_mutex_lock(&mutex_);
    }
    void unlock()
    {
        (void)::pthread_mutex_unlock(&mutex_);
    }
private:
    friend class posix_event;
    ::pthread_mutex_t mutex_;
};

} // asio
} // wsb

#endif