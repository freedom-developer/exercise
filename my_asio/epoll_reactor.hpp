#ifndef WSB_EPOLL_REACTOR_HPP
#define WSB_EPOLL_REACTOR_HPP

#include <mutex>

#include "scheduler_operation.hpp"
#include "scheduler.hpp"

class epoll_reactor
{
public:
    enum op_types { read_op = 0, write_op = 1, connect_op = 1, except_op = 2, max_ops = 3};
    class descriptor_state : scheduler_operation
    {
        descriptor_state *next_, *prev_;

    };

private:
    scheduler& scheduler_;
    std::mutex mutex_;
    
    int epoll_fd_;
    bool shutdown_;

}


#endif