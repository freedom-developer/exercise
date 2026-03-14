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
    { // 先解锁，再通知
        assert(lock.locked());
        state_ |= 1;
        bool have_waiters = (state_ > 1);
        lock.unlock();
        if (have_waiters)
            ::pthread_cond_signal(&cond_);
    }

    template <typename Lock>
    void unlock_and_signal_one_for_destruction(Lock& lock)
    { // 先通知，再解锁
        assert(lock.locked());
        state_ |= 1;
        if (state_ > 1) 
            ::pthread_cond_signal(&cond_);
        lock.unlock();
    }

    template <typename Lock>
    bool maybe_unlock_and_signal_one(Lock& lock)
    { // 如有等待者，则先解锁后通知，并返回true;否则返回false
        assert(lock.locked());
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
        assert(lock.locked());
        (void)lock;
        state_ &= ~std::size_t(1); // state_第一位置0
    }

    template <typename Lock>
    void wait(Lock& lock)
    {
        assert(lock.locked());
        while ((state_ & 1) == 0) { // 注意通知发出后，state_第一位始终为1
            state_ += 2;
            ::pthread_cond_wait(&cond_, &lock.mutex().mutex_); // 等待过程中是解锁状态
            state_ -= 2; // 等待结束时，仍然是锁状态
        }
    }

    template <typename Lock>
    bool wait_for_usec(Lock& lock, long usec)
    { // 微秒级等待
        assert(lock.locked());
        if ((state_ & 1) == 0) {
            state_ += 2;
            timespec ts;
            if (::clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
                ts.tv_sec += usec / 1000000;
                ts.tv_nsec += (usec % 1000000) * 1000;
                ts.tv_sec += ts.tv_nsec / 1000000000;
                ts.tv_nsec = ts.tv_nsec % 1000000000;
                ::pthread_cond_timedwait(&cond_, &lock.mutex().mutex_, &ts); // Ignore EINVAL.
            }
            state_ -= 2;
        }
        return (state_ & 1) != 0; // 被通知后state_&1不为0，否则为0
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