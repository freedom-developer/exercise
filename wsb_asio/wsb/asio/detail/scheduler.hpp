#ifndef WSB_ASIO_DETAIL_SCHEDULER_HPP
#define WSB_ASIO_DETAIL_SCHEDULER_HPP

#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/thread_context.hpp>
#include <wsb/asio/detail/conditionally_enabled_mutex.hpp>
#include <wsb/asio/detail/conditionally_enabled_event.hpp>

namespace wsb {
namespace asio {
namespace detail {

class scheduler : public wsb::asio::execution_context_service_base<scheduler>, public thread_context {
public:
    inline scheduler(execution_context& ctx, int concurrency_hint, bool own_thread);

    inline void shutdown();

private:
    const bool one_thread_;
    mutable conditionally_enabled_mutex mutex_;
    conditionally_enabled_event wakeup_event_;
};

}
}
}

#include <wsb/asio/detail/impl/scheduler.ipp>

#endif