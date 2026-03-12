#ifndef WSB_SYSTEM_DETAIL_GENERIC_CATEGORY_HPP
#define WSB_SYSTEM_DETAIL_GENERIC_CATEGORY_HPP

#include <cstring>
#include <string>

namespace wsb {
namespace system {
namespace detail {

inline char const * strerror_r_helper(const char *r, const char *) noexcept
{
    return r;
}
inline const char * strerror_r_helper(int r, const char *buffer) noexcept
{
    return r == 0 ? buffer : "Unknown error";
}
inline const char * generic_error_category_message(int ev, char *buffer, std::size_t len) noexcept
{
    return strerror_r_helper(strerror_r(ev, buffer, len), buffer);
}

inline std::string generic_error_category_message(int ev)
{
    char buffer[256] = { 0 };
    return generic_error_category_message(ev, buffer, sizeof(buffer));
}

}
}
}


#endif