#ifndef WSB_THREAD_INFO_BASE_HPP
#define WSB_THREAD_INFO_BASE_HPP

#include <climits>
#include <cstddef>

class thread_info_base
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
            this_thread->reusable_memory_[Purpose::mmeindex] = 0;
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
    

    
private:
    enum { chunk_size = 4 };
    enum { max_mem_index = 3 };
    void *reusable_memory_[max_mem_index];
};

#endif