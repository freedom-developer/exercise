#ifndef WSB_SYSTEM_ERROR_CODE_HPP
#define WSB_SYSTEM_ERROR_CODE_HPP

#include <algorithm>
#include <string>

#include <wsb/system/detail/generic_category.hpp>

namespace wsb {
namespace system {


class error_category {
public:
    error_category(error_category const &) = delete;
    error_category& operator=(error_category const &) = delete;

protected:
    ~error_category() = default;
    constexpr error_category() noexcept: id_(0) {}
    explicit constexpr error_category(unsigned long id) noexcept: id_(id) {}

public:
    virtual const char *name() const noexcept = 0;
    virtual std::string message(int ev) const noexcept = 0;
    virtual const char *message(int ev, char *buffer, std::size_t len) const noexcept = 0;
    constexpr bool failed(int ev) const noexcept { return ev != 0; }

    constexpr bool operator==(const error_category& rhs) const noexcept
    {
        return rhs.id_ == 0 ? this == &rhs : id_ == rhs.id_;
    }
    constexpr bool operator!=(const error_category& rhs) const noexcept
    {
        return !(*this == rhs);
    }
    constexpr bool operator<(const error_category& rhs) const noexcept
    {
        if (id_ < rhs.id_) return true;
        if (id_ > rhs.id_) return false;
        // id_相等时且不为0时，表示相等
        if (rhs.id_ != 0) return false; // equal
        // id_相等肯为0时，比较各自的地址
        return std::less<error_category const *>()(this, &rhs); // 先构建一个结构变量()，再调用()运行符
    }

private:
    unsigned long id_;
};

class generic_error_category : public error_category {
public:
    constexpr generic_error_category() noexcept : error_category( (((unsigned long)0xB2AB117A) << 32) + 0x257EDF0D ) {}
    const char *name() const noexcept override
    {
        return "generic";
    }

    std::string message(int ev) const noexcept override
    {
        return detail::generic_error_category_message(ev);
    }

    const char * message(int ev, char *buffer, std::size_t len) const noexcept override
    {
        return detail::generic_error_category_message(ev, buffer, len);
    }
};

class system_error_category : public error_category {
public:
    constexpr system_error_category() noexcept : error_category((((unsigned long)0x8FAFD21E)<<32) + 0x25C5E09B) {}
    const char *name() const noexcept override
    {
        return "system";
    }

    std::string message(int ev) const noexcept override
    {
        return detail::generic_error_category_message(ev);
    }

    const char * message(int ev, char *buffer, std::size_t len) const noexcept override
    {
        return detail::generic_error_category_message(ev, buffer, len);
    }
};

namespace detail {

// 声明
template<class T> struct cat_holder {
    static constexpr system_error_category system_category_instance{};
    static constexpr generic_error_category generic_category_instance{};
};

// 定义
template<class T> constexpr system_error_category cat_holder<T>::system_category_instance;
template<class T> constexpr generic_error_category cat_holder<T>::generic_category_instance;


}

constexpr error_category const & system_category() noexcept
{
    return detail::cat_holder<void>::system_category_instance;
}

constexpr error_category const & generic_category() noexcept
{
    return detail::cat_holder<void>::generic_category_instance;
}

class error_code {
private:
    int val_;
    bool failed_;
    const error_category *cat_;

public:
    constexpr error_code() noexcept : val_(0), failed_(false), cat_(&system_category()) {}
    constexpr error_code(int val, const error_category & cat) noexcept : val_(val), failed_(cat.failed(val)), cat_(&cat) {}

    std::string message() const { return cat_->message(val_); }
    const char * message(char *buffer, std::size_t len) const noexcept { return cat_->message(val_, buffer, len); }
    constexpr bool failed() const noexcept { return failed_; }
};


}
}

#endif