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
    error_code(): err_code(0), err_msg("") {}
    error_code(int code) : err_code(code) { what(); }
    const char *what() const throw()
    {
        if (err_msg.empty() && err_code != 0) {
            char buf[1024] = { 0 };
            strerror_r(err_code, buf, sizeof(buf));
            err_msg = buf;
        }

        return err_msg.c_str();
    }

private:
    int err_code;
    mutable std::string err_msg;
};

}
}


#endif