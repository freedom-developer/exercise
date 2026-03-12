#ifndef WSB_ASIO_DETAIL_SCOPED_LOCK_HPP
#define WSB_ASIO_DETAIL_SCOPED_LOCK_HPP

#include <wsb/asio/detail/noncopyable.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename Mutex>
class scoped_lcok : private noncopyable {
private:
    Mutex& mutex_;
    bool locked_;

public:
    enum adopt_lock_t { adopt_lock };
    scoped_lcok(Mutex& m, adopt_lock_t) : mutex_(m), locked_(true) {}
    explicit scoped_lcok(Mutex& m) : mutex_(m) { mutex_.lock(); locked_ = true; }
    
    ~scoped_lcok()
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