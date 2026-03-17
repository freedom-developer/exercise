#ifndef WSB_ASIO_DETAIL_SCHEDULER_HPP
#define WSB_ASIO_DETAIL_SCHEDULER_HPP

#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/thread_context.hpp>
#include <wsb/asio/detail/conditionally_enabled_mutex.hpp>
#include <wsb/asio/detail/conditionally_enabled_event.hpp>
#include <wsb/asio/detail/op_queue.hpp>
#include <wsb/asio/detail/scheduler_operation.hpp>

#include <atomic>

namespace wsb {
namespace asio {
namespace detail {

class epoll_reactor;

class scheduler : public wsb::asio::execution_context_service_base<scheduler>, public thread_context {
public:
    inline scheduler(execution_context& ctx, int concurrency_hint = 0, bool own_thread = true);

    inline void shutdown(); // 必须实现此虚函数

    inline void post_deferred_completions(op_queue<scheduler_operation>& ops);

    inline void compensating_work_started();

    inline std::size_t run(wsb::system::error_code& ec);
    inline void stop();

private:
    inline void stop_all_threads(conditionally_enabled_mutex::scoped_lock& lock);

    const bool one_thread_;
    mutable conditionally_enabled_mutex mutex_;
    conditionally_enabled_event wakeup_event_;
    epoll_reactor* task_;
    bool stopped_;
    bool task_interrupted_;

    std::atomic<long> outstanding_work_;
};

}
}
}

#include <wsb/asio/detail/epoll_reactor.hpp>
#include <wsb/asio/detail/impl/scheduler.ipp>

#endif