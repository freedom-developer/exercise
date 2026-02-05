#ifndef WSB_EVENTFD_SELECT_INTERRUPTER_HPP
#define WSB_EVENTFD_SELECT_INTERRUPTER_HPP

class eventfd_select_interrupter
{
public:
    inline eventfd_select_interrupter() { open_descriptors(); }
    inline ~eventfd_select_interrupter() { close_descriptors(); }
    inline void recreate();
    inline void interrupt();
    inline bool reset();

    int read_descriptor() const { return read_descriptor_; }
    

private:
    inline void open_descriptors();
    inline void close_descriptors();
    int read_descriptor_;
    int write_descriptor_;
};

#include "eventfd_select_interrupter.ipp"

#endif