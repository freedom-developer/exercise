#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("wushengbang");
MODULE_DESCRIPTION("A simple Linux kernel module");
MODULE_VERSION("0.1");

struct proc_dir_entry *test_pde;
const char *test_name = "test";

int data;
const char *test_string = "this is a test string.";
int arr_data[] = {1, 2, 3, 10, 100, 1000, 3000, 20};

static void *ad_start(struct seq_file *m, loff_t *pos)
{
    *pos = 1;
    return (void *)&arr_data[0];
}

static void *ad_next(struct seq_file *m, void *v, loff_t *pos)
{
    if (*pos >= sizeof(arr_data) / sizeof(int)) return NULL;
    return (void *)&arr_data[*pos++];
}

static void ad_stop(struct seq_file *m, void *v)
{

}

static int ad_show(struct seq_file *m, void *_data)
{
    seq_printf(m, "%d\t", *(int *)_data);
    return 0;
}


struct seq_operations ad_ops = {
    .start = ad_start,
    .next = ad_next,
    .stop = ad_stop,
    .show = ad_show,
};


// _data 必为NULL
static int show_single_data(struct seq_file *m, void *_data)
{
    seq_printf(m, "%d\n", data);
    return 0;
}

static int show_single_string(struct seq_file *m, void *_data)
{
    const struct file *filp = m->file;
    struct inode *inode = filp->f_inode;
    const char *p = (const char *)inode->i_private;
    seq_printf(m, "%s\n", p);
    return 0;
}

static int __init procfs_init(void) {
    printk(KERN_INFO "Hello, kernel world!\n");
    test_pde = proc_mkdir(test_name, NULL);
    if (!test_pde) return -1;

    data = 1009;
    struct proc_dir_entry *single_file = proc_create_single_data("data", 0444, test_pde, show_single_data, NULL);
    if (!single_file) return -1;

    struct proc_dir_entry *test_string_pde = proc_create_single_data("test_string", 0444, test_pde, show_single_string, (void *)test_string);
    if (!test_string_pde) return -1;

    struct proc_dir_entry *arr_data_pde = proc_create_seq("arr_data", 0444, test_pde, &ad_ops);
    if (!arr_data_pde) return -1;

    return 0;
}

static void __exit procfs_exit(void) {
    printk(KERN_INFO "Goodbye, kernel world!\n");
    proc_remove(test_pde);
}

module_init(procfs_init);
module_exit(procfs_exit);
