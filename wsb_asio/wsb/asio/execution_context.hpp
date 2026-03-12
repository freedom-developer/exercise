#ifndef WSB_ASIO_EXECUTION_CONTEXT_HPP
#define WSB_ASIO_EXECUTION_CONTEXT_HPP

#include <wsb/asio/detail/noncopyable.hpp>

namespace wsb {
namespace asio {

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

protected:

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
    inline virtual void notify_fork(execution_context::fork_event event);
    struct key
    {
        key() : type_info_(0), id_(0) {}
        const std::type_info* type_info_;
        const execution_context::id* id_;
    } key_; // 由两个地址组成
    
    execution_context& owner_;
    service* next_;
};

}
}

#include <wsb/asio/impl/execution_context.ipp>

#endif