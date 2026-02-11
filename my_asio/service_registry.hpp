#ifndef WSB_SERVICE_REGISTRY_HPP
#define WSB_SERVICE_REGISTRY_HPP

#include "noncopyable.hpp"
#include "execution_context.hpp"
#include "posix_mutex.hpp"
#include "conditionally_enabled_mutex.hpp"

#include <vector>

namespace wsb {
namespace asio {

class io_contex;

template <typename T>
class typeid_wrapper {};

class service_registry : private noncopyable
{
public:
    service_registry(execution_context& owner): owner_(owner), first_service_(0) {}
    ~service_registry() {}
    void shutdown_services()
    {
        execution_context::service* service = first_service_;
        while (service)
        {
            service->shutdown();
            service = service->next_;
        }
    }
    
    void destroy_services()
    {
        while (first_service_)
        {
            execution_context::service* next_service = first_service_->next_;
            destroy(first_service_);
            first_service_ = next_service;
        }
        
    }

    void notify_fork(execution_context::fork_event fork_ev)
    {
        std::vector<execution_context::service*> services;
        {
            posix_mutex::scoped_lock lock(mutex_);
            execution_context::service* service = first_service_;
            while (service) {
                services.push_back(service);
                service = service->next_;
            }
        }

        std::size_t num_services = services.size();
        if (fork_ev == execution_context::fork_prepare)
            for (std::size_t i = 0; i < num_services; i++)
                services[i]->notify_fork(fork_ev);
        else
            for (std::size_t i = num_services; i > 0; --i)
                services[i - 1]->notify_fork(fork_ev);
    }

    template <typename Service>
    Service& use_service()
    {
        execution_context::service::key key;
        init_key<Service>(key, 0);
        factory_type factory = &service_registry::create<Service, execution_context>;
        return *static_cast<Service*>(do_use_service(key, factory, &owner_));
    }

    template <typename Service>
    Service& use_service(io_context& owner)
    {
        execution_context::service::key key;
        init_key<Service>(key, 0);
        factory_type factory = &service_registry::create<Service, io_contex>;
        return *static_cast<Service*>(do_use_service(key, factory, &owner));
    }
    
    template <typename Service>
    void add_service(Service* new_service)
    {
        execution_context::service::key key;
        init_key<Service>(key, 0);
        return do_add_service(key, new_service);
    }

    template <typename Service>
    bool has_service() const
    {
        execution_context::service::key key;
        init_key<Service>(key, 0);
        return do_has_service(key);
    }

private:
    template <typename Service>
    static void init_key(execution_context::service::key& key, ...)
    {
        init_key_from_id(key, Service::id);
    }

    static void init_key_from_id(execution_context::service::key& key, const execution_context::id& id)
    {
        key.type_info_ = 0;
        key.id_ = &id;
    }

    static bool keys_match(const execution_context::service::key& key1, const execution_context::service::key& key2)
    {
        if (key1.id_ && key2.id_)
            if (key1.id_ == key2.id_)
                return true;
        if (key1.type_info_ && key2.type_info_)
            if (*key1.type_info_ == *key2.type_info_)
                return true;
        return false;
    }

    typedef execution_context::service*(*factory_type)(void*);
    
    template <typename Service, typename Owner>
    static execution_context::service* create(void* owner)
    {
        return new Service(*static_cast<Owner*>(owner)); // new Service(Owner)
    }

    static void destroy(execution_context::service* service)
    {
        delete service;
    }
    
    struct auto_service_ptr;
    friend struct auto_service_ptr;
    struct auto_service_ptr
    {
        execution_context::service* ptr_;
        ~auto_service_ptr() { destroy(ptr_); }
    };

    execution_context::service* do_use_service(const execution_context::service::key& key, factory_type factory, void* owner)
    {
        posix_mutex::scoped_lock lock(mutex_);
        execution_context::service* service = first_service_;
        while (service) {
            if (keys_match(service->key_, key))
                return service;
            service = service->next_;
        }
        lock.unlock();

        auto_service_ptr new_service = { factory(owner) };
        new_service.ptr_->key_ = key;
        lock.lock();
        service = first_service_;
        while (service) {
            if (keys_match(service->key_, key))
                return service;
            service = service->next_;
        }
        new_service.ptr_->next_ = first_service_;
        first_service_ = new_service.ptr_;
        new_service.ptr_ = 0;
        return first_service_;
    }

    void do_add_service(const execution_context::service::key& key, execution_context::service* new_service)
    {
        if (&owner_ != &new_service->context())
            throw(invalid_service_owner());
        
        posix_mutex::scoped_lock lock(mutex_);
        execution_context::service* service = first_service_;
        while (service) {
            if (keys_match(service->key_, key))
                throw(service_already_exists());
            service = service->next_;
        }
        new_service->key_ = key;
        new_service->next_ = first_service_;
        first_service_ = new_service;
    }

    bool do_has_service(const execution_context::service::key& key) const
    {
        posix_mutex::scoped_lock lock(mutex_);
        execution_context::service* service = first_service_;
        while (service) {
            if (keys_match(service->key_, key))
                return true;
            service = service->next_;
        }
        return false;
    }

    mutable posix_mutex mutex_;
    execution_context& owner_;
    execution_context::service* first_service_;
};

}
}

#endif