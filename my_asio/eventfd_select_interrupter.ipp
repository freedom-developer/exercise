#include <sys/eventfd.h>
#include <error.h>
#include "error_code.hpp"


void eventfd_select_interrupter::open_descriptors()
{
    write_descriptor_ = read_descriptor_ = ::eventfd(0, EFD_CLOEXEC | EFD_NOBLOCK);
    if (write_descriptor_ == -1) {
        throw(error_code(errno, system_category()));
    }
}

void eventfd_select_interrupter::close_descriptors()
{
    if (write_descriptor_ != -1)
        ::close(write_descriptor_);
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
    for (;;) {
        uint64_t counter(0);
        errno = 0;
        int bytes_read = ::read(read_descriptor_, &counter, sizeof(uint64_t));
        if (bytes_read < 0 && errno == EINTR)
            continue;
        return true;
    }
}
