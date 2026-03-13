#ifndef WSB_ASIO_DETAIL_CONDITIONALLY_ENABLED_EVENT_HPP
#define WSB_ASIO_DETAIL_CONDITIONALLY_ENABLED_EVENT_HPP

#include <wsb/asio/detail/noncopyable.hpp>
#include <wsb/asio/detail/posix_event.hpp>

namespace wsb {
namespace asio {
namespace detail {

class conditionally_enabled_event : private noncopyable {
public:

private:
    posix_event event;

};

}
}
}


#endif