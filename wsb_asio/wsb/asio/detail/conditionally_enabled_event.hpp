#ifndef WSB_ASIO_DETAIL_CONDITIONALLY_ENABLED_EVENT_HPP
#define WSB_ASIO_DETAIL_CONDITIONALLY_ENABLED_EVENT_HPP

#include <wsb/asio/detail/noncopyable.hpp>
#include <wsb/asio/detail/posix_event.hpp>
#include <wsb/asio/detail/conditionally_enabled_mutex.hpp>

namespace wsb {
namespace asio {
namespace detail {

class conditionally_enabled_event : private noncopyable {
public:
    conditionally_enabled_event() {}
    ~conditionally_enabled_event() {}

    void signal(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            event_.signal(lock);
    }

    void signal_all(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            event_.signal_all(lock);
    }

    void unlock_and_signal_one(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_) 
            event_.unlock_and_signal_one(lock);
    }

    void unlock_and_signal_one_destruction(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            event_.unlock_and_signal_one_for_destruction(lock);
    }

    bool maybe_unlock_and_signal_one(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            return event_.maybe_unlock_and_signal_one(lock);
        else
            return false;
    }

    void clear(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            event_.clear(lock);
    }

    void wait(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            event_.wait(lock);
    }

    bool wait_for_usec(conditionally_enabled_mutex::scoped_lock& lock, long usec)
    {
        if (lock.mutex_.enabled_)
            return event_.wait_for_usec(lock, usec);
        return false;
    }

private:
    posix_event event_;

};

}
}
}


#endif