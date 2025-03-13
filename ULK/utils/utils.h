#ifndef _ULK_COMMON_H
#define _ULK_COMMON_H

int create_syscall(unsigned long syscall_addr);
int remove_syscall(int nr);

#endif