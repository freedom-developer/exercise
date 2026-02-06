#ifndef WSB_POSIX_THREAD_HPP
#define WSB_POSIX_THREAD_HPP

#include <pthread.h>


inline void *posix_thread_function(void *arg);

class posix_thread 
{
public:
    template<typename Function>
    inline posix_thread(Function f, unsigned int  = 0) : joined_(false) 
    {
        start_thread(new func<Function>(f));
    }
    inline ~posix_thread() {
        if (!joined_) {
            ::pthread_detach(thread_);
        }
    }

    inline void join();
    
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
    private:
        Function f_;
    };

    struct auto_func_base_ptr
    {
        func_base *ptr;
        ~auto_func_base_ptr() { delete ptr; }
    };
    

    inline void start_thread(func_base *arg);

    ::pthread_t thread_;
    bool joined_;
};


#include "posix_thread.ipp"

#endif