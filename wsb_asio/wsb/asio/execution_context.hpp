#ifndef WSB_ASIO_EXECUTION_CONTEXT_HPP
#define WSB_ASIO_EXECUTION_CONTEXT_HPP


namespace wsb {
namespace asio {

class execution_context
{
public:
    class service;
};


class execution_context::service
{

};

template <typename Type>
class reactive_context_service_base : public execution_context::service
{

};

}
}



#endif