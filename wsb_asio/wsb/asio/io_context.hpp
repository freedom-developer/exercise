#ifndef WSB_ASIO_IO_CONTEXT_HPP
#define WSB_ASIO_IO_CONTEXT_HPP

#include <cstddef>
#include <wsb/asio/execution_context.hpp>

namespace wsb {
namespace asio {

class io_context : public execution_context {
public:
    inline io_context();
    inline ~io_context();
    inline std::size_t run();
};

}
}

#include <wsb/asio/impl/io_context.ipp>

#endif