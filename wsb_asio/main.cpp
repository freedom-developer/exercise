#include <wsb/asio.hpp>

using namespace wsb::asio;

int main(int argc, char **argv)
{
    io_context ctx;
    
    ctx.run();

    return 0;
}

