#ifndef WSB_SCHEDULER_THREAD_INFO_HPP
#define WSB_SCHEDULER_THREAD_INFO_HPP

#include "op_queue.hpp"

class scheduler;
class scheduler_operation;

struct scheduler_thread_info : public thread_info_base
{
    op_queue<scheduler_operation> private_op_queue;
    long private_outstanding_work;
};

#endif