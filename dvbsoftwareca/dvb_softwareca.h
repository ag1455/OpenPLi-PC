#include <linux/wait.h>
#include <linux/proc_fs.h>

#define MAX_CA_DEVICES 16
#define nums2minor(num,id)   ((num << 2) | id)

#define dvblb_debug 0
#define info(format, arg...) printk(KERN_INFO __FILE__ ": " format "\n" "", ## arg)
#define dprintk if (dvblb_debug) printk

struct ca_device {
	int adapter_num;
	int device_num;
	int minor;
	int users;
};
