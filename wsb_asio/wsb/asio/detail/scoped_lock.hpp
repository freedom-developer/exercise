#ifndef WSB_ASIO_DETAIL_SCOPED_LOCK_HPP
#define WSB_ASIO_DETAIL_SCOPED_LOCK_HPP

#include <wsb/asio/detail/noncopyable.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename Mutex>
class scoped_lock : private noncopyable {
private:
    Mutex& mutex_;
    bool locked_;

public:
    enum adopt_lock_t { adopt_lock };
    scoped_lock(Mutex& m, adopt_lock_t) : mutex_(m), locked_(true) {}
    explicit scoped_lock(Mutex& m) : mutex_(m) { mutex_.lock(); locked_ = true; }
    
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

    bool locked() const
    {
        return locked_;
    }
};

}
}
}


#endif