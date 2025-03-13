#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>



static int __init demo_init(void)
{
    printk("demo init\n");   

    return 0;
}



static void __exit demo_exit(void)
{
    printk("demo_exit\n");

}

module_init(demo_init);
module_exit(demo_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("shengbangwu");
MODULE_DESCRIPTION("demo");
