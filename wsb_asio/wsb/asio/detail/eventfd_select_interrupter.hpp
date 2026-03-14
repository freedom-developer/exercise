#ifndef WSB_ASIO_DETAIL_EVENTFD_SELECT_INTERRUPTER_HPP
#define WSB_ASIO_DETAIL_EVENTFD_SELECT_INTERRUPTER_HPP

namespace wsb {
namespace asio {
namespace detail {

class eventfd_select_interrupter {
public:
    inline eventfd_select_interrupter();
    inline ~eventfd_select_interrupter();

    inline void recreate();

    inline void interrupt();

    inline bool reset();

    int read_descriptor() const { return read_descriptor_; }

private:
    inline void open_descriptors();
    inline void close_descriptors();

    int read_descriptor_;
    int write_descriptor_;
};

}
}
}


#include <wsb/asio/detail/impl/eventfd_select_interrupter.ipp>

#endif