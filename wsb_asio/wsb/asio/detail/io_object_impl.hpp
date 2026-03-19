#ifndef WSB_ASIO_DETAIL_IO_OBJECT_IMPL_HPP
#define WSB_ASIO_DETAIL_IO_OBJECT_IMPL_HPP

#include <type_traits>

namespace wsb {
namespace asio {
namespace detail {

template <typename IoObjectService, typename Executor>
class io_object_impl
{
public:
    typedef typename IoObjectService::implementation_type implementation_type;
    // template <typename ExecutionContext>
    // explicit io_object_impl(ExecutionContext& context, 
    //     typename std::enable_if<std::is_convertible<ExecutionContext&, execution_context&>::value>::type* = 0)
    // : service_()
    // {
    //     service_->construct(implementation_);
    // }

private:
    IoObjectService* service_;
    implementation_type implementation_;
};

}
}
}



#endif