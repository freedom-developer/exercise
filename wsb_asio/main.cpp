#include <wsb/asio.hpp>
#include <iostream>


using namespace wsb::asio;
using namespace wsb::asio::ip;

int main(int argc, char **argv)
{
    io_context ctx;

    tcp::acceptor acceptor_(ctx, tcp::endpoint(tcp::v4(), 8888));
    // asseprot_.async_accept(...);
    
    ctx.run();

    return 0;
}

