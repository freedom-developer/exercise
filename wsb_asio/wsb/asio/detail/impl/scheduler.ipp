#ifndef WSB_ASIO_DETAIL_SCHEDULER_IPP
#define WSB_ASIO_DETAIL_SCHEDULER_IPP

#include <wsb/asio/detail/scheduler.hpp>

namespace wsb {
namespace asio {
namespace detail {

scheduler::scheduler(execution_context& ctx, int concurrency_hint, bool own_thread) 
: wsb::asio::execution_context_service_base<scheduler>(ctx),
one_thread_(true),
mutex_(false)
{

}

void scheduler::shutdown()
{
    
}

void scheduler::post_deferred_completions(op_queue<scheduler_operation>& ops)
{

}

void scheduler::compensating_work_started()
{
    
}

}
}
}

#endif