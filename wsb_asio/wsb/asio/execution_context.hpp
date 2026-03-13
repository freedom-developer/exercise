#ifndef WSB_ASIO_EXECUTION_CONTEXT_HPP
#define WSB_ASIO_EXECUTION_CONTEXT_HPP

#include <wsb/asio/detail/noncopyable.hpp>

namespace wsb {
namespace asio {

class io_context;

namespace detail {

class service_registry;

}

class execution_context : private noncopyable {
public:
    class id;
    class service;

public:
    inline execution_context();
    inline ~execution_context();

public:
    enum fork_event { fork_prepare, fork_parent, fork_child };
    inline void notify_fork(fork_event ev);

    template <typename Service>
    friend Service& use_service(execution_context& e);

    template <typename Service>
    friend Service& use_service(io_context& ioc);

    template <typename Service, typename... Args>
    friend Service& make_service(execution_context&e, Args&&... args);

    template <typename Service>
    friend void add_service(execution_context& e, Service* svc);

    template <typename Service>
    friend bool has_service(execution_context& e);

protected:
    inline void shutdown();
    inline void destroy();

private:
    detail::service_registry* service_registry_;
};


class execution_context::id : private noncopyable {
public:
    id() {}
};

class execution_context::service : private noncopyable {
public:
    execution_context& context();

protected:
    inline service(execution_context& owner);
    inline virtual ~service();

private:
    friend class detail::service_registry;
    virtual void shutdown() = 0;
    inline virtual void notify_fork(execution_context::fork_event event) {}
    struct key
    {
        key() : type_info_(0), id_(0) {}
        const std::type_info* type_info_;
        const execution_context::id* id_;
    } key_; // 由两个地址组成
    
    execution_context& owner_;
    service* next_;
};

template <typename Type>
class service_id : public execution_context::id {

};

template <typename Type>
class execution_context_service_base : public execution_context::service {
public:
    static service_id<Type> id;
    execution_context_service_base(execution_context& e) : execution_context::service(e) {}
};

template <typename Type>
service_id<Type> execution_context_service_base<Type>::id;

}
}

#include <wsb/asio/impl/execution_context.hpp>
#include <wsb/asio/impl/execution_context.ipp>

#endif