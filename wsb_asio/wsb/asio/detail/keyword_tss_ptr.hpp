#ifndef WSB_ASIO_DETAIL_KEYWORD_TSS_PTR_HPP
#define WSB_ASIO_DETAIL_KEYWORD_TSS_PTR_HPP

#include <wsb/asio/detail/noncopyable.hpp>

namespace wsb {
namespace asio {
namespace detail {

template <typename T>
class keyword_tss_ptr : private noncopyable {
public:
    keyword_tss_ptr() {}
    ~keyword_tss_ptr() {}
    operator T*() const { return value_; }
    void operator=(T* value) { value_ = value; }

private:
    static __thread T* value_;
};

// 定义模板类中的静态成员变量
template <typename T>
__thread T* keyword_tss_ptr<T>::value_;

}
}
}


#endif