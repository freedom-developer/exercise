#ifndef WSB_TIMER_QUEUE_SET_HPP
#define WSB_TIMER_QUEUE_SET_HPP

#include "timer_queue_base.hpp"

namespace wsb {
namespace asio {

class timer_queue_set
{
public:
    inline timer_queue_set(): first_(0) {}
    inline void insert(timer_queue_base* q)
    {
        q->next_ = first_;
        first_ = q;
    }

    inline void erase(timer_queue_base* q)
    {
        if (first_) {
            if (q == first_) {
                first_ = q->next_;
                q->next_ = 0;
                return;
            }
            for (timer_queue_base* p = first_; p->next_; p = p->next_) {
                if (p->next_ == q) {
                    p->next_ = q->next_;
                    q->next_ = 0;
                    return;
                }
            }
        }
    }

    inline bool all_empty() const
    {
        for (timer_queue_base* p = first_; p; p = p->next_) {
            if (!p->empty())
                return false;
        }
        return true;
    }

    inline long wait_duration_msec(long max_duration) const
    {
        long min_duration = max_duration;
        for (timer_queue_base* p = first_; p; p = p->next_)
            min_duration = p->wait_duration_msec(min_duration);
        return min_duration;
    }

    inline long wait_duration_usec(long max_duration) const
    {
        long min_duration = max_duration;
        for (timer_queue_base* p = first_; p; p = p->next_)
            min_duration = p->wait_duration_usec(min_duration);
        return min_duration;
    }

    inline void get_ready_timers(op_queue<scheduler_operation>& ops)
    {
        for (timer_queue_base* p = first_; p; p = p->next_)
            p->get_ready_timers(ops);
    }

    inline void get_all_timers(op_queue<scheduler_operation>& ops)
    {
        for (timer_queue_base* p = first_; p; p = p->next_)
            p->get_all_timers(ops);
    }

private:
    timer_queue_base* first_;
};

} // asio
} // namespace wsb

#endif