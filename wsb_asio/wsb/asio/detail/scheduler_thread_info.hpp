#ifndef WSB_ASIO_DETAIL_SCHEDULER_THREAD_INFO_HPP
#define WSB_ASIO_DETAIL_SCHEDULER_THREAD_INFO_HPP

#include <wsb/asio/detail/thread_info_base.hpp>
#include <wsb/asio/detail/op_queue.hpp>


namespace wsb {
namespace asio {
namespace detail {

class scheduler;
class scheduler_operation;
struct scheduler_thread_info : public thread_info_base
{
    op_queue<scheduler_operation> private_op_queue;
    long private_outstanding_work;
};



}
}
}


#endif