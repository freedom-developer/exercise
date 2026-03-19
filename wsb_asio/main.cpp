#include <iostream>
#include <wsb/asio.hpp>

using namespace wsb::asio;
using namespace wsb::asio::ip;

static const std::string SEND_MSG = "hello";
static const char *ip_str = "127.0.0.1";
static unsigned short port = 7890;

class TcpClient
{
public:
    TcpClient(io_context &ioc)
        : sock_(ioc)
    {
        // tcp::endpoint ep(make_address(ip_str), port);
        // sock_.async_connect(ep, [this](const boost::system::error_code &ec) {
        //     on_connect(ec);
        // });
    }

private:
    void on_connect(const wsb::system::error_code &ec)
    {
        // if (ec) {
        //     std::cerr << "connect failed: " << ec.message() << std::endl;
        //     return;
        // }
        // std::cout << "connected" << std::endl;

        // async_write(sock_, buffer(SEND_MSG),
        //             [this](const boost::system::error_code &ec, std::size_t len) {
        //                 on_write(ec, len);
        //             });
    }

    void on_write(const wsb::system::error_code &ec, std::size_t)
    {
        // if (ec) {
        //     std::cerr << "write failed: " << ec.message() << std::endl;
        //     return;
        // }
        // std::cout << "sent: " << SEND_MSG << std::endl;

        // async_read(sock_, buffer(recv_buf_, SEND_MSG.size()),
        //            [this](const boost::system::error_code &ec, std::size_t len) {
        //                on_read(ec, len);
        //            });
    }

    void on_read(const wsb::system::error_code &ec, std::size_t len)
    {
        // if (ec) {
        //     std::cerr << "read failed: " << ec.message() << std::endl;
        //     return;
        // }
        // std::cout << "server replied: " << std::string(recv_buf_, len) << std::endl;
        // sock_.close();
    }

    tcp::socket sock_;
    char recv_buf_[64]{};
};

int main()
{
    io_context ioc;
    TcpClient client(ioc);
    ioc.run();
    return 0;
}