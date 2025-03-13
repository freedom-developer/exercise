#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>

#include <linux/interrupt.h>
#include <linux/irq.h>

unsigned int irq_no = 1;
void *dev_id = (void *)0x100;
int success = 0;

irqreturn_t demo_interrupt(int irq, void *dev_id)
{
    printk("demo_interrupt\n");
    return IRQ_HANDLED;
}

static int __init demo_init(void)
{
    printk("demo init\n");   
    int ret = request_irq(irq_no, demo_interrupt, IRQF_TRIGGER_FALLING, "demo", dev_id);
    if (ret == 0)
        success = 1;
    else
        success = 0;
    printk("request irq success = %d\n", success);

    return 0;
}



static void __exit demo_exit(void)
{
    printk("demo_exit\n");
    if (success)
        free_irq(irq_no, dev_id);
}

module_init(demo_init);
module_exit(demo_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("shengbangwu");
MODULE_DESCRIPTION("demo");
