#ifndef WSB_ASIO_DETAIL_IMPL_EVENTFD_SELECT_INTERRUPTER_HPP
#define WSB_ASIO_DETAIL_IMPL_EVENTFD_SELECT_INTERRUPTER_HPP

#include <wsb/asio/detail/eventfd_select_interrupter.hpp>
#include <wsb/system/error_code.hpp>

#include <sys/eventfd.h>
#include <unistd.h>
#include <fcntl.h>

namespace wsb {
namespace asio {
namespace detail {

eventfd_select_interrupter::eventfd_select_interrupter()
{
    open_descriptors();
}

eventfd_select_interrupter::~eventfd_select_interrupter()
{
    close_descriptors();
}

void eventfd_select_interrupter::recreate()
{
    close_descriptors();
    write_descriptor_ = -1;
    read_descriptor_ = -1;
    open_descriptors();
}

void eventfd_select_interrupter::interrupt()
{
    uint64_t counter(1UL);
    int result = ::write(write_descriptor_, &counter, sizeof(uint64_t));
    (void)result;
}

bool eventfd_select_interrupter::reset()
{
    if (write_descriptor_ == read_descriptor_) {
        for (;;) {
            uint64_t count(0);
            errno = 0;
            int bytes_read = ::read(read_descriptor_, &count, sizeof(uint64_t));
            if (bytes_read < 0 && errno == EINTR) 
                continue;
            return true;
        }
    } else {
        for (;;) {
            char data[1024];
            int bytes_read = ::read(read_descriptor_, data, sizeof(data));
            if (bytes_read == sizeof(data)) continue;
            if (bytes_read > 0) return true;
            if (bytes_read == 0) return false;
            if (errno == EINTR) continue;
            if (errno == EWOULDBLOCK || errno == EAGAIN) return true;
            return false;
        }
    }
}



void eventfd_select_interrupter::open_descriptors()
{
    write_descriptor_ = read_descriptor_ = ::eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
    if (read_descriptor_ == -1 && errno == EINVAL) {
        write_descriptor_ = read_descriptor_ = ::eventfd(0, 0);
        if (read_descriptor_ != -1) {
            ::fcntl(read_descriptor_, F_SETFL, O_NONBLOCK);
            ::fcntl(write_descriptor_, F_SETFL, O_NONBLOCK);
        }
    }
    if (read_descriptor_ == -1) {
        int pid_fds[2];
        if (pipe(pid_fds) == 0) {
            read_descriptor_ = pid_fds[0];
            write_descriptor_ = pid_fds[1];
            ::fcntl(read_descriptor_, F_SETFL, O_NONBLOCK);
            ::fcntl(write_descriptor_, F_SETFL, O_NONBLOCK);
            ::fcntl(read_descriptor_, F_SETFD, FD_CLOEXEC);
            ::fcntl(write_descriptor_, F_SETFD, FD_CLOEXEC);
        } else {
            wsb::system::error_code ec(errno, wsb::system::system_category());
            throw(ec);
        }
    }
}

void eventfd_select_interrupter::close_descriptors()
{
    if (read_descriptor_ != -1)
        ::close(read_descriptor_);
    if (write_descriptor_ != -1)
        ::close(write_descriptor_);
}

}
}
}


#endif