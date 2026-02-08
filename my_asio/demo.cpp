#include "posix_thread.hpp"

#include <iostream>

using namespace std;

int main(void)
{
    wsb::asio::posix_thread pt([]() { cout << "Test posix thread\n"; });
    pt.join();

    return 0;
}