#ifndef WSB_SCOPED_LOCK_HPP
#define WSB_SCOPED_LOCK_HPP

#include "noncopyable.hpp"

namespace wsb {
namespace asio {

template <typename Mutex>
class scoped_lock : private noncopyable
{
public:
    enum adopt_lock_t { adopt_lock_t };
    scoped_lock(Mutex& m, adopt_lock_t): mutex_(m), locked_(true) {}
    
    explicit scoped_lock(Mutex& m): mutex_(m)
    {
        mutex_.lock();
        locked_ = true;
    }

    ~scoped_lock()
    {
        if (locked_)
            mutex_.unlock();
    }

    void lock()
    {
        if (!locked_) {
            mutex_.lock();
            locked_ = true;
        }
    }

    void unlock()
    {
        if (locked_) {
            mutex_.unlock();
            locked_ = false;
        }
    }

    bool locked() const { return locked_; }

    Mutex& mutex() { return mutex_; }
private:
    Mutex& mutex_;
    bool locked_;
};

}
}

#endif