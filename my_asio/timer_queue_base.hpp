#ifndef WSB_TIMER_QUEUE_BASE_HPP
#define WSB_TIMER_QUEUE_BASE_HPP

#include "op_queue.hpp"
#include "scheduler_operation.hpp"

namespace wsb {
namespace asio {

class timer_queue_base
{
public:
    timer_queue_base(): next_(0) {}
    virtual ~timer_queue_base() {}
    virtual bool empty() const = 0;
    virtual long wait_duration_msec(long max_duration) const = 0;
    virtual long wait_duration_usec(long max_duration) const = 0;
    virtual void get_ready_timers(op_queue<scheduler_operation>& ops) = 0;
    virtual void get_all_timers(op_queue<scheduler_operation>& ops) = 0;
private:
    friend class timer_queue_set;
    timer_queue_base* next_;
};

}
}

#endif