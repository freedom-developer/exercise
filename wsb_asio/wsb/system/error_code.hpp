#ifndef WSB_SYSTEM_ERROR_CODE_HPP
#define WSB_SYSTEM_ERROR_CODE_HPP

#include <exception>
#include <string>
#include <cerrno>
#include <cstring>

namespace wsb {
namespace system {

class error_code : public std::exception 
{
public:
    error_code(): code_(0), msg_("") {}
    error_code(int code) : code_(code) { what(); }
    error_code(int code, const std::string& msg) : code_(code), msg_(msg) {}
    const char *what() const throw()
    {
        if (msg_.empty() && code_ != 0) {
            char buf[1024] = { 0 };
            strerror_r(code_, buf, sizeof(buf));
            msg_ = buf;
        }

        return msg_.c_str();
    }

private:
    int code_;
    mutable std::string msg_;
};

}
}


#endif