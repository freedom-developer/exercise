#include "error_code.hpp"

void posix_thread::start_thread(func_base *arg)
{
    auto error = ::pthread_create(&thread_, 0, posix_thread_function, arg);
    if (error != 0) {
        delete arg;
        error_code ec(error, system_category());
        throw(ec);
    }   
}

void *posix_thread_function(void *arg)
{
    posix_thread::auto_func_base_ptr func = { static_cast<posix_thread::func_base*>(arg) };
    func.ptr->run();
    return 0;
}

void posix_thread::join()
{
    if (!joined_) {
        ::pthread_join(thread_, 0);
        joined_ = true;
    }
}