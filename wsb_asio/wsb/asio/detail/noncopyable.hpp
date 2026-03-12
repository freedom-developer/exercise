#ifndef WSB_ASIO_DETAIL_NONCOPYABLE_HPP
#define WSB_ASIO_DETAIL_NONCOPYABLE_HPP

namespace wsb {
namespace asio {
namespace detail {

class noncopyable {
protected:
    noncopyable() {}
    ~noncopyable() {}
private:
    noncopyable(const noncopyable&);
    const noncopyable& operator=(const noncopyable&);
};

}

// 将detail::noncopyable导致到wsb::asio空间中，使在wsb::asio命名空间中使用noncopyable时，不必指出noncopyable所属的命名空间
using wsb::asio::detail::noncopyable;

}
}

#endif