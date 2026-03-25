#ifndef WSB_ASIO_EXECUTION_CONTEXT_HPP
#define WSB_ASIO_EXECUTION_CONTEXT_HPP

#include <wsb/asio/detail/service_registry.hpp>

namespace wsb {
namespace asio {

class execution_context
{
public:
    class id;
    class service;

private:
    wsb::asio::detail::service_registry* service_registry_;
};

// 只用于定义一个空类型及其地址
class execution_context::id
{
public:
  id() {}
};

/// Base class for all io_context services.
class execution_context::service
{
public:
//   execution_context& context();

protected:
//   BOOST_ASIO_DECL service(execution_context& owner);

//   BOOST_ASIO_DECL virtual ~service();

private:
  virtual void shutdown() = 0;

//   inline virtual void notify_fork(execution_context::fork_event event);

  friend class wsb::asio::detail::service_registry;
  struct key
  {
    key() : type_info_(0), id_(0) {}
    const std::type_info* type_info_;
    const execution_context::id* id_;
  } key_;

  execution_context& owner_;
  service* next_;
};

template <typename Type>
class reactive_context_service_base : public execution_context::service
{

};

}
}



#endif