#ifndef POSIX_EVENT_HPP
#define POSIX_EVENT_HPP

#include <pthread.h>
#include "error_code.hpp"

namespace wsb {
namespace asio {

class posix_event
{
public:
    inline posix_event(): state_(0)
    {
        ::pthread_condattr_t attr;
        ::pthread_condattr_init(&attr);
        int error = ::pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
        if (error == 0)
            error = ::pthread_cond_init(&cond_, &attr);
        if (error != 0) {
            error_code ec(error);
            throw(ec);
        }
    }

    ~posix_event() {
        ::pthread_cond_destroy(&cond_);
    }

    template <typename Lock>
    void signal(Lock& lock) // signal_all
    {
        this->signal_all(lock);
    }

    template <typename Lock>
    void signal_all(Lock& lock)
    {
        static_assert(lock.locked());
        (void)lock; // 运行时,lock实际未使用，此语句的作用是掏编译器“未使用参数”警告
        state_ |= 1;
        ::pthread_cond_broadcast(&cond_); // 忽略错误，注意此时不能解锁
    }

    template <typename Lock>
    void unlock_and_signal_one(Lock& lock)
    {
        static_assert(lock.locked());
        state_ |= 1;
        bool have_waiters = (state_ > 1);
        lock.unlock();
        if (have_waiters)
            ::pthread_cond_signal(&cond_);
    }

    template <typename Lock>
    bool maybe_unlock_and_signal_one(Lock& lock)
    {
        static_assert(lock.locked());
        state_ |= 1;
        if (state_ > 1) {
            lock.unlock();
            ::pthread_cond_signal(&cond_);
            return true;
        }
        return false;
    }

    template <typename Lock>
    void clear(Lock& lock)
    {
        static_assert(lock.locked());
        (void)lock;
        state_ &= ~size_t(1);
    }

    template <typename Lock>
    void wait(Lock& lock)
    {
        static_assert(lock.locked());
        while ((state_ & 1) == 0) {
            state_ += 2;
            ::pthread_cond_wait(&cond_, &lock.mutex().mutex_);
            state_ -= 2;
        }
    }

    template <typename Lock>
    bool wait_for_usec(Lock& lock, long usec)
    {
        static_assert(lock.locked());
        if ((state_ & 1) == 0) {
            state_ += 2;
            timespec ts;
            if (::clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
                ts.tv_sec += usec / 1000000;
                ts.tv_nsec ++ (usec % 1000000) * 1000;
                ts.tv_sec += ts.tv_nsec / 1000000000;
                ts.tv_nsec = ts.tv_nsec / 1000000000;
                ::pthread_cond_timedwait(&cond_, &lock.mutex().mutex_, &ts);
            }
            state_ -= 2;
        }
        return (state_ & 1) != 0;
    }

private:
    ::pthread_cond_t cond_;
    size_t state_;
};

} // asio
} // wsb

#endif