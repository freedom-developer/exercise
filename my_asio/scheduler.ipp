#include "scheduler.hpp"

scheduler::scheduler(): thread_(0) {}

scheduler::~scheduler()
{
    if (thread_) {
        thread_->join();
        delete thread_;
    }
}