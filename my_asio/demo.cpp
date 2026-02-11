#include "posix_thread.hpp"
#include "conditionally_enabled_mutex.hpp"
#include "conditionally_enabled_event.hpp"

#include <iostream>
#include <unistd.h>

using namespace std;
using namespace wsb::asio;

typedef conditionally_enabled_mutex wsb_mtx;
typedef conditionally_enabled_event wsb_event;

wsb_mtx mtx(true);
wsb_event event;

void th_func1(void)
{
    wsb_mtx::scoped_lock lock(mtx);
    event.wait_for_usec(lock, 2000000);

    cout << "th_func is running.\n";
}

int main(void)
{
    posix_thread pt(th_func1);
    sleep(1);
    // {
        // wsb_mtx::scoped_lock lock(mtx);
        // event.signal(lock);
    // }
    pt.join();

    return 0;
}