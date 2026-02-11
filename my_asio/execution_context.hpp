#ifndef WSB_EXECUTION_CONTEXT_HPP
#define WSB_EXECUTION_CONTEXT_HPP

#include <stdexcept>

#include "noncopyable.hpp"

namespace wsb {
namespace asio {

class execution_context;
class io_context;
class service_registry;

class execution_context : private noncopyable
{
public:
    class id;
    class service;
    inline execution_context();
    inline ~execution_context();

protected:
    inline void shutdown();
    inline void destroy();

public:
    enum fork_event {
        fork_prepare,
        fork_parent,
        fork_child
    };

    inline void notify_fork(fork_event event);

    template <typename Service>
    friend Service& use_service(execution_context& e);

    template <typename Service>
    friend Service& use_service(io_context& ioc); // 在io_context.hpp中定义

    template <typename Service>
    friend void add_service(execution_context& e, Service* svc);

    template <typename Service>
    friend bool has_service(execution_context&  e);

private:
    service_registry* service_registry_;
};

class execution_context::id : private noncopyable
{
public:
    id() {}
};

class execution_context::service : private noncopyable
{
public:
    execution_context& context() { return owner_; }
protected:
    service(execution_context& owner): owner_(owner), next_(0) {}
    virtual ~service() {}
private:
    virtual void shutdown() = 0;
    virtual void notify_fork(execution_context::fork_event event) {}
    friend class service_registry;
    struct  key
    {
        key() : type_info_(0), id_(0) {}
        const std::type_info* type_info_;
        const execution_context::id* id_;
    } key_;
    execution_context& owner_;
    service* next_;
};

class service_already_exists : public std::logic_error
{
public:
    inline service_already_exists(): std::logic_error("Service already exists.") {}
};

class invalid_service_owner : public std::logic_error
{
public:
    inline invalid_service_owner(): std::logic_error("Invalid service owner.") {}
};


template <typename Type>
class service_id : public execution_context::id
{

};

template <typename Type>
class execution_context_service_base : public execution_context::service
{
public:
    static service_id<Type> id;
    execution_context_service_base(execution_context& e) : execution_context::service(e) {}
};

template <typename Type>
service_id<Type> execution_context_service_base<Type>::id;

}
}

#endif