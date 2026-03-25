#ifndef WSB_ASIO_DETAIL_IO_OBJECT_IMPL_HPP
#define WSB_ASIO_DETAIL_IO_OBJECT_IMPL_HPP

#include <type_traits>

#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/io_object_executor.hpp>

namespace wsb {
namespace asio {
namespace detail {

// IoObjectService = reactive_socket_service<tcp>
// Executor = executor
template <typename IoObjectService, typename Executor>
class io_object_impl
{
public:
    // implementation_type = reactive_socket_service<tcp>::implementation_type
    typedef typename IoObjectService::implementation_type implementation_type;

    template <typename ExecutionContext>
    explicit io_object_impl(ExecutionContext& context, 
        typename std::enable_if<std::is_convertible<ExecutionContext&, execution_context&>::value>::type* = 0)
    : service_(&wsb::asio::use_service<IoObjectService>(context)),
      implementation_executor(context.get_executor(), std::is_same<ExecutionContext, io_context>::value)
    {
        service_->construct(implementation_);
    }

private:
    IoObjectService* service_;
    implementation_type implementation_;
    io_object_executor<Executor> implementation_executor;
};

}
}
}



#endif