#include <linux/module.h>
#include <linux/init.h>
#include <linux/kallsyms.h> // kallsyms_lookup_name
#include <linux/syscalls.h> // SYSCALL_DEFINEx
#include <linux/moduleparam.h>
#include <linux/wait.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/kernel.h>
#include <asm/unistd.h>

#ifndef NR_syscalls
#define NR_syscalls 333
#endif

int demo_wait_nr = -1;
int demo_wakeup_nr = -1;

module_param(demo_wait_nr, int, 0444); // 只读
module_param(demo_wakeup_nr, int, 0444); // 只读

DECLARE_WAIT_QUEUE_HEAD(demo_wait_queue);
int demo_wait_condition = 0;

int sc_stat[NR_syscalls];
unsigned long old_scs[NR_syscalls];

// 系统调用的实现
asmlinkage long demo_wait(void)
{
    printk("demo_wait called\n");
    
    // 条件变量为假时，等待
    return wait_event_interruptible(demo_wait_queue, demo_wait_condition);
}

// 系统调用的实现
asmlinkage long demo_wakeup(void)
{
    printk("demo_wakeup called\n");
    
    // 唤醒等待队列
    demo_wait_condition = 1;
    wake_up_interruptible(&demo_wait_queue);

    return 0;
}



// 内核线程的实现
int thread_fn(void *data)
{
    printk("demo_thread started\n");
    while (!kthread_should_stop()) {
        printk("demo_thread running\n");
        msleep(1000);
    }
    printk("demo_thread stopped\n");
    return 0;
}

struct task_struct *kthread_demo = NULL;

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

static int __init demo_init(void)
{
    int ret;

    printk("demo init\n");   

    // 新建系统调用
    // if ((ret = create_syscall((unsigned long)demo_wait)) < 0) {
    //     printk("create_syscall demo_wait failed\n");
    //     return -1;
    // }
    // demo_wait_nr = ret;
    // if ((ret = create_syscall((unsigned long)demo_wakeup)) < 0) {  
    //     printk("create_syscall demo_wakeup failed\n");
    //     return -1;
    // }
    // demo_wakeup_nr = ret;
    // printk("demo_wait_nr = %d, demo_wakeup_nr = %d\n", demo_wait_nr, demo_wakeup_nr);

    // 创建一个内核线程
    kthread_demo = kthread_run(thread_fn, NULL, "kthread_demo");
    if (IS_ERR(kthread_demo)) {
        printk("kthread_run failed\n");
        return -1;
    }
    printk("kthread_demo = %p\n", kthread_demo);

    return 0;
}



static void __exit demo_exit(void)
{
    printk("demo_exit\n");

    // 移除系统调用
    if (demo_wait_nr > 0) {
        remove_syscall(demo_wait_nr);
    }
    if (demo_wakeup_nr > 0) {
        remove_syscall(demo_wakeup_nr);
    }

    // 移除内核线程
    if (kthread_demo) {
        kthread_stop(kthread_demo);
        kthread_demo = NULL;
    }

}

module_init(demo_init);
module_exit(demo_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("shengbangwu");
MODULE_DESCRIPTION("demo");
