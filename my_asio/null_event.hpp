#ifndef NULL_EVENT_HPP
#define NULL_EVENT_HPP

#include <unistd.h>
#include <sys/select.h>

namespace wsb {
namespace asio {

class null_event
{
public:
    null_event() {}
    ~null_event() {}
    
    template <typename Lock>
    void signal(Lock&) {}

    template <typename Lock>
    void signal_all(Lock&) {}

    template <typename Lock>
    void unlock_and_signal_one(Lock&) {}

    template <typename Lock>
    bool maybe_unlock_and_signal_one(Lock&) { return false; }

    template <typename Lock>
    void clear(Lock&) {}

    template <typename Lock>
    void wait(Lock&) { do_wait(); }

    template <typename Lock>
    bool wait_for_usec(Lock&, long usec)
    {
        do_wait_for_usec(usec);
        return true;
    }
    
private:
    inline static void do_wait()
    {
        pause();
    }

    inline static void do_wait_for_usec(long usec)
    {
        timeval tv;
        tv.tv_sec = usec / 1000000;
        tv.tv_usec = usec % 1000000;
        ::select(0, 0, 0, 0, &tv);
    }
};

}
}

#endif