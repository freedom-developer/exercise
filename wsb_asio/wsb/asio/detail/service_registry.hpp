#ifndef WSB_ASIO_DETAIL_SERVICE_REGISTRY_HPP
#define WSB_ASIO_DETAIL_SERVICE_REGISTRY_HPP

#include <wsb/asio/detail/noncopyable.hpp>
#include <wsb/asio/execution_context.hpp>
#include <wsb/asio/detail/posix_mutex.hpp>
#include <wsb/asio/io_context.hpp>

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

    template <typename Service>
    Service& use_service(io_context& owner);

    template <typename Service>
    void add_service(Service* new_service);

    template <typename Service>
    bool has_service() const;

private:
    template <typename Service>
    static void init_key(execution_context::service::key& key, ...);
    
    inline static void init_key_from_id(execution_context::service::key& key, const execution_context::id& id);

    inline static bool keys_match(const execution_context::service::key& key1, const execution_context::service::key& key2);

    typedef execution_context::service*(*factory_type)(void*);

    template <typename Service, typename Owner>
    static execution_context::service* create(void *owner); // 以owner为参数构建一个Service对象

    inline static void destroy(execution_context::service* service);

    struct auto_service_ptr;
    friend struct auto_service_ptr;
    struct auto_service_ptr {
        execution_context::service* ptr_;
        ~auto_service_ptr() { destroy(ptr_); }
    };

    inline execution_context::service* do_use_service(const execution_context::service::key& key, factory_type factory, void *owner);
    inline void do_add_service(const execution_context::service::key& key, execution_context::service* new_service);
    inline bool do_has_service(const execution_context::service::key& key) const;


    mutable posix_mutex mutex_;
    execution_context& owner_;
    execution_context::service* first_service_;

};

}
}
}

#include <wsb/asio/detail/impl/service_registry.hpp>
#include <wsb/asio/detail/impl/service_registry.ipp>

#endif