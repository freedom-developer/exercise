#ifndef WSB_NONCOPYABLE_HPP
#define WSB_NONCOPYABLE_HPP

namespace wsb {
namespace asio {

class noncopyable
{
protected:
    noncopyable() {}
    ~noncopyable() {}

private:
    noncopyable(const noncopyable&);
    noncopyable& operator=(const noncopyable&);
};

}
}


#endif