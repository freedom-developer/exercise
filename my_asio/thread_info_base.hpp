#ifndef WSB_THREAD_INFO_BASE_HPP
#define WSB_THREAD_INFO_BASE_HPP

#include <climits>
#include <cstddef>

#include "op_queue.hpp"
#include "noncopyable.hpp"

namespace wsb {
namespace asio {

class thread_info_base : private noncopyable
{
public:
    struct default_tag
    {
        enum { mem_index = 0 };
    };
    struct awaitable_frame_tag
    {
        enum { mem_index = 1 };
    };

    struct executor_function_tag
    {
        enum { mem_index = 2 };
    };

    thread_info_base()
    {
        for (int i = 0; i < max_mem_index; i++)
            reusable_memory_[i] = 0;
    }
    ~thread_info_base()
    {
        for (int i = 0; i < max_mem_index; i++)
            ::operator delete(reusable_memory_[i]);
    }

    static void* allocate(thread_info_base* this_thead, size_t size)
    {
        return allocate(default_tag(), this_thead, size);
    }

    template <typename Purpose>
    static void* allocate(Purpose, thread_info_base* this_thread, size_t size)
    {
        size_t chunks = (size + chunk_size - 1) / chunk_size;
        if (this_thread && this_thread->reusable_memory_[Purpose::mem_index]) {
            void *const pointer = this_thread->reusable_memory_[Purpose::mem_index];
            this_thread->reusable_memory_[Purpose::mem_index] = 0;
            unsigned char *const mem = static_cast<unsigned char*>(pointer);
            if (static_cast<size_t>(mem[0]) >= chunks) {
                mem[size] = mem[0];
                return pointer;
            }
            ::operator delete(pointer);
        }
        void* const pointer = ::operator new(chunks * chunk_size + 1);
        unsigned char* const mem = static_cast<unsigned char *>(pointer);
        mem[size] = (chunks <= UCHAR_MAX) ? static_cast<unsigned char>(chunks) : 0;
        return pointer;
    }
    
    static void deallocate(thread_info_base* this_thread, void *pointer, size_t size)
    {
        return deallocate(default_tag(), this_thread, pointer, size);
    }

    template <typename Purpose>
    static void deallocate(Purpose, thread_info_base* this_thread, void* pointer, size_t size)
    {
        if (size <= chunk_size * UCHAR_MAX) {
            if (this_thread && this_thread->reusable_memory_[Purpose::mem_index] == 0) {
                unsigned char* const mem = static_cast<unsigned char*>(pointer);
                mem[0] = mem[size];
                this_thread->reusable_memory_[Purpose::mem_index] = pointer;
                return;
            }
        }
        ::operator delete(pointer);
    }
    
private:
    enum { chunk_size = 4 };
    enum { max_mem_index = 3 };
    void *reusable_memory_[max_mem_index];
};

class scheduler_operation;
struct scheduler_thread_info : public thread_info_base
{
    op_queue<scheduler_operation> private_op_queue;
    long private_outstanding_work;
};

} // asio
} // wsb

#endif