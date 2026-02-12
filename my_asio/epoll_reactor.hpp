#ifndef EPOLL_REACTOR_HPP
#define EPOLL_REACTOR_HPP

#include "scheduler_operation.hpp"
#include "conditionally_enabled_mutex.hpp"
#include "op_queue.hpp"
#include "reactor_op.hpp"
#include "object_pool.hpp"
#include "timer_queue_set.hpp"
#include "eventfd_select_interrupter.hpp"
#include "scheduler.hpp"
#include "execution_context.hpp"


namespace wsb {
namespace asio {

class epoll_reactor : public execution_context_service_base<epoll_reactor>
{
public:
    enum op_types {
        read_op = 0,
        write_op = 1,
        connect_op = 1,
        except_op = 2,
        max_ops = 3
    };

    class descriptor_state : scheduler_operation
    {
        friend class epoll_reactor;
        friend class object_pool_access;
        descriptor_state* next_;
        descriptor_state* prev_;
        conditionally_enabled_mutex mutex_;   
        epoll_reactor* reactor_;
        int descriptor_;
        uint32_t registered_events_;
        op_queue<reactor_op> op_queue_[max_ops]; // 每个描述符有3个操作队列，读、写、异常
        bool try_speculative_[max_ops];
        bool shutdown_;

        inline descriptor_state(bool locking);
        void set_ready_events(uint32_t events) { task_result_ = events; }
        void add_ready_events(uint32_t events) { task_result_ |= events; }
        inline scheduler_operation* perform_io(uint32_t events);
        inline static void do_complete(void *owner, scheduler_operation* base, const error_code& ec, std::size_t bytes_transfered);
    };
    typedef descriptor_state* descriptor_data;

    inline epoll_reactor(execution_context& ctx);
    inline ~epoll_reactor();
    inline void shutdown();
    inline void notify_fork(execution_context::fork_event fork_ev);
    inline void init_task();
    inline int register_descriptor(int descriptor, descriptor_data& data);
    inline int register_internal_descriptor(int op_type, int descriptor, descriptor_data& data, reactor_op* op);
    inline void move_descriptor(int descriptor, descriptor_data& target_data, descriptor_data& source_data);

    void post_immediate_completion(reactor_op* op, bool is_continuation)
    {
        scheduler_.post_immediate_completion(op, is_continuation);
    }

    inline void start_op(int op_type, int descriptor, descriptor_data& data, reactor_op* op, bool is_continuation, bool allow_speculative);
    inline void cancel_ops(int descriptor, descriptor_data& data);
    inline void deregister_descriptor(int descriptor, descriptor_data& data, bool closing);
    inline void deregister_internal_descriptor(int descriptor, descriptor_data& data);


private:
    enum { epoll_size = 20000 };
    inline static int do_epoll_create();
    inline static int do_timerfd_create();
    inline descriptor_state* allocate_descriptor_sate();
    inline void free_descriptor_state(descriptor_state* s);
    inline void do_add_timer_queue(timer_queue_base& queue);
    inline void do_remove_timer_queue(timer_queue_base& queue);
    inline void update_timeout();
    inline int get_timeout(int msec);
    inline int get_timeout(itimerspec& ts);
    
    scheduler& scheduler_;
    conditionally_enabled_mutex mutex_;
    eventfd_select_interrupter interrupter_;
    int epoll_fd_;
    int timer_fd_;
    timer_queue_set timer_queues_;
    bool shutdown_;
    conditionally_enabled_mutex registered_descriptors_mutex_;
    object_pool<descriptor_state> registered_descriptors_;
    struct perform_io_cleanup_on_block_exit;
    friend struct perform_io_cleanup_on_block_exit;
};

}
}


#endif