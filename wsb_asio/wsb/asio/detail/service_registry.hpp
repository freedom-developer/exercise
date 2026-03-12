#ifndef WSB_ASIO_DETAIL_SERVICE_REGISTRY_HPP
#define WSB_ASIO_DETAIL_SERVICE_REGISTRY_HPP

#include <wsb/asio/detail/noncopyable.hpp>
#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/posix_mutex.hpp>

namespace wsb {
namespace asio {
namespace detail {

class service_registry : private noncopyable {
public:
    inline service_registry(execution_context& owner);
    inline ~service_registry();

    inline void shutdown_services(); // 关闭所有服务：遍历所有服务，执行其shutdown操作
    inline void destroy_services(); // 销毁所有服务: delete first_service_中的所有服务
    inline void notify_fork(execution_context::fork_event fork_ev);

    template <typename Service>
    Service& use_service();

private:
    template <typename Service>
    static void init_key(execution_context::service::key& key, ...);

    
    inline static void init_key_from_id(execution_context::service::key& key, const execution_context::id& id);

    inline static void destroy(execution_context::service* service);

    posix_mutex mutex_;
    execution_context& owner_;
    execution_context::service* first_service_;

};

}
}
}

#include <wsb/asio/detail/impl/service_registry.ipp>

#endif