#ifndef WSB_EVENTFD_SELECT_INTERRUPTER_HPP
#define WSB_EVENTFD_SELECT_INTERRUPTER_HPP

#include <sys/eventfd.h>
#include <unistd.h>
#include <fcntl.h>

#include "error_code.hpp"


namespace wsb {
namespace asio {

class eventfd_select_interrupter
{
public:
    inline eventfd_select_interrupter() { open_descriptors(); }
    inline ~eventfd_select_interrupter() { close_descriptors(); }
    inline void recreate()
    {
        close_descriptors();
        write_descriptor_ = -1;
        read_descriptor_ = -1;
        open_descriptors();
    }

    inline void interrupt()
    {
        uint64_t counter(1UL);
        int result = ::write(write_descriptor_, &counter, sizeof(uint64_t));
        (void)result;
    }

    inline bool reset()
    {
        if (write_descriptor_ == read_descriptor_) {
            for (;;) {
                uint64_t counter(0);
                int bytes_read = ::read(read_descriptor_, &counter, sizeof(uint64_t));
                if (bytes_read < 0 && errno == EINTR)
                    continue;
                return true;
            }
        } else {
            for (;;) {
                char data[1024];
                int bytes_read = ::read(read_descriptor_, data, sizeof(data));
                if (bytes_read == sizeof(data))
                    continue;
                if (bytes_read > 0)
                    return true;
                if (bytes_read == 0)
                    return false;
                if (errno == EINTR)
                    continue;
                if (errno == EWOULDBLOCK || errno == EAGAIN)
                    return true;
                return false;
            }
        }
    }

    int read_descriptor() const { return read_descriptor_; }

private:
    inline void open_descriptors()
    {
        read_descriptor_ = write_descriptor_ = ::eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
        if (read_descriptor_ == -1) {
            int pipe_fds[2];
            if (pipe(pipe_fds) == 0) {
                read_descriptor_ = pipe_fds[0];
                ::fcntl(read_descriptor_, F_SETFL, O_NONBLOCK);
                ::fcntl(read_descriptor_, F_SETFD, FD_CLOEXEC);
                write_descriptor_ = pipe_fds[1];
                ::fcntl(write_descriptor_, F_SETFL, O_NONBLOCK);
                ::fcntl(write_descriptor_, F_SETFD, FD_CLOEXEC);
            } else {
                error_code ec(errno);
                throw(ec);
            }
        }
    }
    inline void close_descriptors()
    {
        if (write_descriptor_ != -1 && write_descriptor_ != read_descriptor_)
            ::close(write_descriptor_);
        if (read_descriptor_ != -1)
            ::close(read_descriptor_);
    }
    int read_descriptor_;
    int write_descriptor_;
}; 

}
}

#endif