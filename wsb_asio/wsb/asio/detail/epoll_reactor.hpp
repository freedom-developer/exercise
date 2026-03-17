#ifndef WSB_ASIO_DETAIL_EPOLL_REACTOR_HPP
#define WSB_ASIO_DETAIL_EPOLL_REACTOR_HPP

#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/eventfd_select_interrupter.hpp>
#include <wsb/asio/detail/timer_queue_set.hpp>
#include <wsb/asio/detail/object_pool.hpp>
#include <wsb/asio/detail/reactor_op.hpp>
#include <wsb/asio/detail/scheduler.hpp>

namespace wsb {
namespace asio {
namespace detail {

class epoll_reactor : public execution_context_service_base<epoll_reactor> {
public:
    enum op_types { read_op = 0, write_op = 1, connect_op = 1, except_op = 2, max_ops = 3 };

    class descriptor_state : scheduler_operation {
        friend class epoll_reactor;
        friend class object_pool_access;

        descriptor_state* next_;
        descriptor_state* prev_;

        conditionally_enabled_mutex mutex_;
        epoll_reactor* reactor_;
        int descriptor_;
        uint32_t registered_events_;
        op_queue<reactor_op> op_queue_[max_ops];
        bool try_speculative_[max_ops];
        bool shutdown_;

        inline descriptor_state(bool locking);
        void set_ready_events(uint32_t events) { task_result_ = events; }
        void add_ready_events(uint32_t events) { task_result_ |= events; }
        inline scheduler_operation* perform_io(uint32_t events);
        inline static void do_complete(void* owner, scheduler_operation* base, const wsb::system::error_code& ec, std::size_t bytes_transferred);
    };

    typedef descriptor_state* per_descriptor_data;
    
    inline epoll_reactor(wsb::asio::execution_context& ctx);

    inline ~epoll_reactor();

    inline void interrupt();


private:
    enum { epoll_size = 20000 };

    inline static int do_epoll_create();
    inline static int do_timerfd_create();

    inline per_descriptor_data allocate_descriptor_state();

    // 修改这里：使用detail命名空间中的scheduler，而不是前向声明嵌套类
    scheduler& scheduler_;
    
    conditionally_enabled_mutex mutex_;
    eventfd_select_interrupter interrupter_;
    int epoll_fd_;
    int timer_fd_;
    timer_queue_set timer_queues_;
    bool shutdown_;
    conditionally_enabled_mutex registered_descriptors_mutex_;
    object_pool<descriptor_state> registered_descriptors_;

    // Helper class to do post-perform_io cleanup.
    struct perform_io_cleanup_on_block_exit;
    friend struct perform_io_cleanup_on_block_exit;

};

}
}
}

#include <wsb/asio/detail/impl/epoll_reactor.ipp>


#endif