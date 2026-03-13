#ifndef WSB_ASIO_DETAIL_TSS_PTR_HPP
#define WSB_ASIO_DETAIL_TSS_PTR_HPP

#include <wsb/asio/detail/keyword_tss_ptr.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename T>
class tss_ptr : keyword_tss_ptr<T> {
public:
    void operator=(T* value)
    {
        keyword_tss_ptr<T>::operator=(value);
    }
};

}
}
}


#endif