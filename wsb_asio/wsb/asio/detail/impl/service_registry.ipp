#ifndef WSB_ASIO_DETAIL_IMPL_SERVICE_REGISTRY_IPP
#define WSB_ASIO_DETAIL_IMPL_SERVICE_REGISTRY_IPP

#include <wsb/asio/detail/service_registry.hpp>

#include <vector>

namespace wsb {
namespace asio {
namespace detail {

service_registry::service_registry(execution_context& owner) : owner_(owner), first_service_(0)
{
}

service_registry::~service_registry()
{
}

void service_registry::shutdown_services()
{
    auto *service = first_service_;
    while (service)
    {
        service->shutdown();
        service = service->next_;
    }
}

void service_registry::destroy_services()
{
    while (first_service_) {
        auto *next_service = first_service_;
        destroy(first_service_);
        first_service_ = next_service;
    }
}

void service_registry::notify_fork(execution_context::fork_event fork_ev)
{
    std::vector<execution_context::service*> services;
    {
        posix_mutex::scoped_lcok lock(mutex_);
        auto *service = first_service_;
        while (service) {
            services.push_back(service);
            service = service->next_;
        }
    }

    auto num_services = services.size();
    if (fork_ev == execution_context::fork_prepare)
        for (std::size_t i = 0; i < num_services; i++)
            services[i]->notify_fork(fork_ev);
    else
        for (std::size_t i = num_services; i > 0; i--)
            services[i - 1]->notify_fork(fork_ev);
}

template <typename Service>
Service& service_registry::use_service()
{
    execution_context::service::key key;
    init_key<Service>(key, 0);
}

void service_registry::init_key_from_id(execution_context::service::key& key, const execution_context::id& id)
{
    key.type_info_ = 0;
    key.id_ = &id;
}




void service_registry::destroy(execution_context::service* service)
{
    delete service;
}

}
}
}


#endif