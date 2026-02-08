#ifndef WSB_ERROR_CODE_HPP
#define WSB_ERROR_CODE_HPP

#include <string>
#include <cstring>

namespace wsb {
namespace asio {

class error_category
{
public:
    error_category( error_category const &) = delete;
    error_category& operator=(error_category const &) = delete;
    virtual const char *name() const noexcept = 0;
    virtual std::string message(int ev) const = 0;
    virtual char const * message(int ev, char *buffer, size_t len) const noexcept = 0;

protected:
    ~error_category() = default;
    constexpr error_category() noexcept: id_(0) {}
    explicit constexpr error_category(uint64_t id) noexcept: id_(id) {}

private:
    uint64_t id_;
};

inline char const * generic_error_category_message(int ev, char *buffer, size_t len) noexcept
{
    return strerror_r(ev, buffer, len);
}

inline std::string generic_error_category_message(int ev)
{
    char buffer[128] = { 0 };
    return generic_error_category_message(ev, buffer, sizeof(buffer));
}

class generic_error_category: public error_category
{
public:
    constexpr generic_error_category() noexcept: error_category( (uint64_t( 0xB2AB117A ) << 32) + 0x257EDF0D ) {}
    const char *name() const noexcept override { return "generic"; }
    inline std::string message(int ev) const override { return generic_error_category_message(ev); }
    inline char const * message(int ev, char *buffer, size_t len) const noexcept override{ return generic_error_category_message(ev, buffer, len); }
};

class system_error_category: public error_category
{
public:
    constexpr system_error_category() noexcept: error_category( (uint64_t(0x8FAFD21E)<<32) + 0x25C5E09B) {}
    const char *name() const noexcept override { return "system"; }
    inline std::string  message(int ev) const override { return generic_error_category_message(ev); }
    inline char const * message(int ev, char *buffer, size_t len) const noexcept override { return generic_error_category_message(ev, buffer, len); }
};

template<class T> struct cat_holder
{
    static constexpr system_error_category system_category_instance{};
    static constexpr generic_error_category generic_category_instance{};
};
template<class T> constexpr system_error_category cat_holder<T>::system_category_instance;
template<class T> constexpr generic_error_category cat_holder<T>::generic_category_instance;

constexpr error_category const & system_category() noexcept
{
    return cat_holder<void>::system_category_instance;
}
constexpr error_category const & generic_category() noexcept
{
    return cat_holder<void>::generic_category_instance;
}

class error_code
{
private:
    int val_;
    const error_category * cat_;
public:
    constexpr error_code() noexcept: val_(0), cat_(&system_category()) {}
    constexpr error_code(int val, const error_category & cat = system_category()) noexcept: val_(val), cat_(&cat) {}
};

} // asio
} // namespace wsb

#endif