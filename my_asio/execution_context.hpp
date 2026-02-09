#ifndef WSB_EXECUTION_CONTEXT_HPP
#define WSB_EXECUTION_CONTEXT_HPP

namespace wsb {
namespace asio {

class execution_context;
class io_context;

class execution_context
{
public:
    class id;
    class service;
    inline execution_context();
    inline ~execution_context();

    enum fork_event {
        fork_prepare,
        fork_parent,
        fork_child
    };

    inline void notify_fork(fork_event event);

    template <typename Service>
    friend Service& use_service(execution_context& e);

    template <typename Service>
    friend Service& use_service(io_context& ioc);

    template <typename Service>
    friend void add_service(execution_context& e, Service* svc);

    template <typename Service>
    friend bool has_service(execution_context&  e);

protected:
    inline void shutdown();
    inline void destroy();
private:
    
};

}
}

#endif