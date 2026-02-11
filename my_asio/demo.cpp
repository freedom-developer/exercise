#include "posix_thread.hpp"
#include "conditionally_enabled_mutex.hpp"
#include "conditionally_enabled_event.hpp"
#include "thread_info_base.hpp"

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
    event.wait_for_usec(lock, 2000);

    cout << "th_func is running.\n";

    thread_info_base ti_base;
    for (int i = 0; i < 10; i++) {
        auto ptr = thread_info_base::allocate(&ti_base, 10);
        cout << "ptr: " << ptr << endl;
        auto ptr2 = thread_info_base::allocate(&ti_base, 10);
        cout << "ptr2: " << ptr2 << endl;
        thread_info_base::deallocate(&ti_base, ptr, 10);
        thread_info_base::deallocate(&ti_base, ptr2, 10);
    }
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