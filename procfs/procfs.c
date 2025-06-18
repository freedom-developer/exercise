#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("wushengbang");
MODULE_DESCRIPTION("A simple Linux kernel module");
MODULE_VERSION("0.1");

struct proc_dir_entry *test_pde;
const char *test_name = "test";


static int __init procfs_init(void) {
    printk(KERN_INFO "Hello, kernel world!\n");
    test_pde = proc_mkdir(test_name, NULL);
    
    return 0;
}

static void __exit procfs_exit(void) {
    printk(KERN_INFO "Goodbye, kernel world!\n");
    proc_remove(test_pde);
}

module_init(procfs_init);
module_exit(procfs_exit);
