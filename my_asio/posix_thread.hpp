#ifndef WSB_POSIX_THREAD_HPP
#define WSB_POSIX_THREAD_HPP

#include <pthread.h>

#include "error_code.hpp"

namespace wsb {
namespace asio {

inline void *posix_thread_function(void *arg);

class posix_thread 
{
public:
    template<typename Function>
    inline posix_thread(Function f, unsigned int = 0) : joined_(false) 
    {
        start_thread(new func<Function>(f));
    }

    inline ~posix_thread() {
        if (!joined_) {
            ::pthread_detach(thread_);
        }
    }

    inline void join()
    {
        if (!joined_) {
            ::pthread_join(thread_, 0);
            joined_ = true;
        }
    }
    
private:
    friend void *posix_thread_function(void *arg);

    class func_base 
    {
    public:
        virtual ~func_base() {}
        virtual void run() = 0;
    };

    template<typename Function>
    class func : public func_base {
    public:
        func(Function f) : f_(f) {}
        void run() override { f_(); }
    private:
        Function f_;
    };

    struct auto_func_base_ptr
    {
        func_base *ptr;
        ~auto_func_base_ptr() { delete ptr; }
    };
    
    inline void start_thread(func_base *arg)
    {
        auto error = ::pthread_create(&thread_, 0, posix_thread_function, arg);
        if (error != 0) {
            delete arg;
            error_code ec(error);
            throw(ec);
        }
    }

    ::pthread_t thread_;
    bool joined_;
};

void *posix_thread_function(void *arg)
{
    posix_thread::auto_func_base_ptr func = { static_cast<posix_thread::func_base*>(arg) };
    func.ptr->run();
    return 0;
}

} // asio
} // wsb

#endif