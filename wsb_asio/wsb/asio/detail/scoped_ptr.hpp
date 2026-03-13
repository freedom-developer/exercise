#ifndef WSB_ASIO_DETAIL_SCOPED_PTR_HPP
#define WSB_ASIO_DETAIL_SCOPED_PTR_HPP


namespace wsb {
namespace asio {
namespace detail {

template <typename T>
class scoped_ptr {
public:
    explicit scoped_ptr(T* p = 0) : p_(p) {}
    ~scoped_ptr() { delete p_; }
    T* get() { return p_; }
    T* operator->() { return p_; }
    T& operator*() { return *p_; }
    void reset(T* p = 0) { delete p_; p_ = p; }
    T* release() { T* tmp = p_; p_ = 0; return tmp; }

private:
    scoped_ptr(const scoped_ptr&);
    scoped_ptr& operator=(const scoped_ptr&);

    T* p_;
};

}
}
}


#endif