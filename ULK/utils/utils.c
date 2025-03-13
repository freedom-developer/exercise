#include <linux/kallsyms.h> // kallsyms_lookup_name
#include <linux/syscalls.h> // NR_syscalls
#include <linux/kernel.h> // printk

#ifndef NR_syscalls
#define NR_syscalls 333

#endif

// 创建一个系统调用
int create_syscall(unsigned long syscall_addr)
{
    // 查找sys_call_table的地址
    unsigned long *sys_call_table = (unsigned long *)kallsyms_lookup_name("sys_call_table");
    if (!sys_call_table) {
        printk("kallsyms_lookup_name failed\n");
        return -1;
    }

    // 查找sys_ni_syscall的地址
    unsigned long sys_ni_syscall = (unsigned long)kallsyms_lookup_name("sys_ni_syscall");
    if (!sys_ni_syscall) {
        printk("kallsyms_lookup_name failed\n");
        return -1;
    }

    // 查找sys_call_table中的空闲位置
    int i = 0;
    for (i = 0; i < NR_syscalls; i++) {
        if (sys_call_table[i] == sys_ni_syscall) {
            break;
        }
    }
    if (i == NR_syscalls) {
        printk("no free syscall\n");
        return -1;
    }

    // 检查sys_call_talbe[i]的读写属性
    unsigned int level;
    pte_t *pte = lookup_address((unsigned long)sys_call_table, &level);
    if (!pte) { //  || level != PG_LEVEL_4K) {
        printk("lookup_address failed, level: %d\n", level);
        return -1;
    }
    pte->pte |= _PAGE_RW; // 修改sys_call_table[i]的读写属性
    sys_call_table[i] = syscall_addr;   // 将sys_call_table[i]指向demo_syscall
    pte->pte &= ~_PAGE_RW; // 恢复sys_call_table[i]的读写属性

    return i;
}

// 移除系统调用
int remove_syscall(int nr)
{
    // 查找sys_call_table的地址
    unsigned long *sys_call_table = (unsigned long *)kallsyms_lookup_name("sys_call_table");
    if (!sys_call_table) {
        printk("kallsyms_lookup_name failed\n");
        return -1;
    }

    // 查找sys_ni_syscall的地址
    unsigned long sys_ni_syscall = (unsigned long)kallsyms_lookup_name("sys_ni_syscall");
    if (!sys_ni_syscall) {
        printk("kallsyms_lookup_name failed\n");
        return -1;
    }

    unsigned int level;
    pte_t *pte = lookup_address((unsigned long)sys_call_table, &level);
    if (!pte) { // || level != PG_LEVEL_4K) {
        printk("lookup_address failed, level: %d\n", level);
        return -1;
    }
    pte->pte |= _PAGE_RW; // 修改sys_call_table[i]的读写属性
    sys_call_table[nr] = sys_ni_syscall;   // 将sys_call_table[i]指向demo_syscall
    pte->pte &= ~_PAGE_RW; // 恢复sys_call_table[i]的读写属性

    return 0;
}
