#ifndef WSB_SCHEDULER_HPP
#define WSB_SCHEDULER_HPP

#include "posix_thread.hpp"

class scheduler
{
public:
    inline scheduler();
    inline ~scheduler();
private:
    posix_thread* thread_;
};


#include "scheduler.ipp"

#endif