#ifndef CONDITIONALLY_ENABLED_EVENT_HPP
#define CONDITIONALLY_ENABLED_EVENT_HPP

#include "posix_event.hpp"
#include "conditionally_enabled_mutex.hpp"
#include "null_event.hpp"

namespace wsb {
namespace asio {
    
class conditionally_enabled_event : private noncopyable
{
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

    bool maybe_unlock_and_signal_one(conditionally_enabled_mutex::scoped_lock& lock)
    {
        if (lock.mutex_.enabled_)
            event_.maybe_unlock_and_signal_one(lock);
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
        else
            null_event().wait(lock);
    }

    bool wait_for_usec(conditionally_enabled_mutex::scoped_lock& lock, long usec)
    {
        if (lock.mutex_.enabled_)
            return event_.wait_for_usec(lock, usec);
        else
            return null_event().wait_for_usec(lock, usec);
    }

private:
    posix_event event_;
};

} // namespace asio 
} // namespace wsb

#endif