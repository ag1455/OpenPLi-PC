/*
 * dvb_softwareca.c
 *
 * DVBSoftwareCA Kernel Module - Copyright cougar 2011
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 * Or, point your browser to http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 *
 *
 * This code is based on the DVBLoopback driver - Alan Nisota 2006
 *
 */

#define DVBSOFTWARECA_VERSION "0.0.4"
#define DVBSOFTWARECA_MAJOR 230

#include <linux/errno.h>
#include <linux/module.h>
#include <linux/cdev.h>
#include <linux/platform_device.h>
#include "dvb_softwareca.h"
#include "ca_netlink.h"
#include "dvbdev.h"

static struct platform_device *dvblb_basedev;
static struct ca_device* ca_devices[MAX_CA_DEVICES];
int devices_counter = 0;
static struct class *dvb_class;
static struct cdev ca_devices_cdev;

struct ca_device* find_device(int minor) {
	int i;

	for(i = 0; i < devices_counter; i++)
		if(ca_devices[i]->minor == minor)
			return ca_devices[i];
	return NULL;
}

static int ca_open(struct inode *inode, struct file *file)
{
	struct ca_device *cadev = find_device(iminor(inode));

	if (!cadev)
		return -ENODEV;
	if (!cadev->users)
		return -EBUSY;

	dprintk("ca_open adapter%d - ca%d\n", cadev->adapter_num, cadev->device_num);

	cadev->users--;
	try_module_get(THIS_MODULE);
	return 0;
}

static int ca_release(struct inode *inode, struct file *f)
{
	struct ca_device *cadev = find_device(iminor(inode));

	if (!cadev) {
		printk("Failed to locate device\n");
		return -EFAULT;
	}

	dprintk("ca_release adapter%d - ca%d\n", cadev->adapter_num, cadev->device_num);

	cadev->users++;

	/*f->private_data = dvbdev;
	ret = dvb_generic_release(inode, f);
	if (ret < 0) {
		goto out;
	}*/

	module_put(THIS_MODULE);
	return 0;
}

#ifdef HAVE_UNLOCKED_IOCTL
static long ca_ioctl(struct file *f,
#else
static int ca_ioctl(struct inode *inode, struct file *f,
#endif
	unsigned int cmd, unsigned long arg)
{
#ifdef HAVE_UNLOCKED_IOCTL
	struct inode *inode = f->f_path.dentry->d_inode;
#endif
	struct ca_device *cadev = find_device(iminor(inode));

	if (!cadev) {
		printk("Failed to locate device\n");
		return -EFAULT;
	}

	dprintk("ca_ioctl adapter%d - ca%d cmd:%x\n", cadev->adapter_num,
			cadev->device_num, cmd);

	if (cmd == CA_SET_DESCR) {
		ca_descr_t *ca_descr = (ca_descr_t *)arg;
		unsigned short ca_num = ((cadev->adapter_num&0xFF)<<8)|(cadev->device_num&0xFF);

		printk("cactl CA_SET_DESCR par %d idx %d %02X...%02X\n",
				ca_descr->parity, ca_descr->index, ca_descr->cw[0], ca_descr->cw[7]);

		netlink_send_cw(ca_num, ca_descr);
		return 0;
	}
	if (cmd == CA_SET_PID) {
		ca_pid_t *ca_pid = (ca_pid_t *)arg;
		unsigned short ca_num = ((cadev->adapter_num&0xFF)<<8)|(cadev->device_num&0xFF);

		printk("cactl CA_SET_PID %04X index %d\n", ca_pid->pid, ca_pid->index);

		netlink_send_pid(ca_num, ca_pid);
		return 0;
	}

	return -EFAULT;
}

static struct file_operations ca_device_fops = {
	.owner		= THIS_MODULE,
	.open		= ca_open,
	.release	= ca_release,
#ifdef HAVE_UNLOCKED_IOCTL
	.unlocked_ioctl = ca_ioctl,
#else
	.ioctl		= ca_ioctl,
#endif
};

static void destroy_ca_device(struct ca_device *cadev)
{
	if (!cadev)
		return;
	device_destroy(dvb_class, MKDEV(DVBSOFTWARECA_MAJOR, cadev->minor));
	kfree (cadev);
}

static int create_ca_device(int adapter_num, int device_num, int global_num)
{
	struct ca_device *cadev;
	struct device *clsdev;
	int minor = nums2minor(adapter_num, device_num);

	cadev = kmalloc(sizeof(struct ca_device), GFP_KERNEL);
	if (!cadev){
		return -ENOMEM;
	}

	cadev->adapter_num = adapter_num;
	cadev->device_num = device_num;
	cadev->minor = minor;
	cadev->users = 1;
	ca_devices[global_num] = cadev;

	clsdev = device_create(dvb_class, NULL,
			MKDEV(DVBSOFTWARECA_MAJOR, minor),
			cadev, "dvb%d.ca%d", adapter_num, device_num);
	if (IS_ERR(clsdev)) {
		printk(KERN_ERR "dvbsoftwareca: failed to create device dvb%d.ca%d (%ld)\n",
			adapter_num, device_num, PTR_ERR(clsdev));
		return PTR_ERR(clsdev);
	}
	printk(KERN_DEBUG "dvbsoftwareca: register adapter%d/ca%d @ minor: %04X\n",
		adapter_num, device_num, minor);

	return 0;
}

static int dvb_uevent(struct device *dev, struct kobj_uevent_env *env)
{
	struct ca_device *cadev = dev_get_drvdata(dev);

	add_uevent_var(env, "DVB_DEVICE_NUM=%d", cadev->device_num);
	add_uevent_var(env, "DVB_ADAPTER_NUM=%d", cadev->adapter_num);
	return 0;
}

static char *dvb_devnode(struct device *dev, umode_t *mode)
{
	struct ca_device *cadev = dev_get_drvdata(dev);

	return kasprintf(GFP_KERNEL, "dvb/adapter%d/ca%d",
		cadev->adapter_num, cadev->device_num);
}

static int __init dvblb_init(void)
{
	int i, j, ret, failed;
	dev_t dev = MKDEV(DVBSOFTWARECA_MAJOR, 0);
	char device_name[50];

	failed=0;

	if ((ret = register_chrdev_region(dev, MAX_CA_DEVICES, "DVBSOFTWARECSA")) != 0) {
		printk(KERN_ERR "dvbsoftwareca: unable to get major %d\n", DVBSOFTWARECA_MAJOR);
		return ret;
	}

	cdev_init(&ca_devices_cdev, &ca_device_fops);

	if ((ret = cdev_add(&ca_devices_cdev, dev, MAX_CA_DEVICES)) != 0) {
		printk(KERN_ERR "dvbsoftwareca: unable register character device\n");
		return ret;
	}

	dvb_class = class_create(THIS_MODULE, "dvbsoftwareca");
	if (IS_ERR(dvb_class)) {
		printk("dvbsoftwareca: unable to create dvb_class\n");
		return PTR_ERR(dvb_class);
	}
	dvb_class->dev_uevent = dvb_uevent;
	dvb_class->devnode = dvb_devnode;

	info("frontend loopback driver v"DVBSOFTWARECA_VERSION);
	printk("dvbsoftwareca: registering adapters\n");

	dvblb_basedev = platform_device_alloc("dvbsoftwareca", -1);
	if (!dvblb_basedev) {
		return -ENOMEM;
	}
	ret = platform_device_add(dvblb_basedev);
	if (ret) {
		platform_device_put(dvblb_basedev);
		return ret;
	}

	ret = register_netlink();
	if (ret) {
		printk("dvbsoftwareca: unable to register netlink socket\n");
		return -EFAULT;
	}

	for(i=0; i < 8; i++) {
		for(j=0; (j<8 && devices_counter<MAX_CA_DEVICES); j++) {
			struct file *filp;
			
			snprintf(device_name, 50, "/dev/dvb/adapter%d/frontend%d", i, j);
			filp = filp_open(device_name,00,O_RDONLY);

			if (!IS_ERR(filp) && filp!=NULL) {
				filp_close(filp, NULL);

				ret = create_ca_device(i, j, devices_counter++);
				if (ret != 0) {
					printk("dvbsoftwareca: Failed to add CA%d device for adapter%d\n", j, i);
					failed = 1;
					break;
				}
				printk("dvbsoftwareca: registered CA%d device for adapter%d\n", j, i);
			}

		}

		if (failed)
			break;
	}

	if (!failed)
		printk("dvbsoftwareca: registered %d CA devices\n", devices_counter);

	if (failed) {
		for(i = 0; i < devices_counter; i++) {
			destroy_ca_device(ca_devices[i]);
		}
		platform_device_unregister(dvblb_basedev);
		cdev_del(&ca_devices_cdev);
		unregister_chrdev_region(dev, MAX_CA_DEVICES);

		return -EFAULT;
	}

	return 0;
}

static void __exit cleanup_dvblb_module(void)
{
	int i;
	printk("Unregistering CA devices");

	for(i = 0; i < devices_counter; i++) {
		destroy_ca_device(ca_devices[i]);
	}

	unregister_netlink();
	class_destroy(dvb_class);

	platform_device_unregister(dvblb_basedev);
	cdev_del(&ca_devices_cdev);
	unregister_chrdev_region(MKDEV(DVBSOFTWARECA_MAJOR, 0), MAX_CA_DEVICES);
}

module_init(dvblb_init);
module_exit(cleanup_dvblb_module);

MODULE_DESCRIPTION("DVB software CA device.");
MODULE_AUTHOR("cougar");
MODULE_LICENSE("GPL");
MODULE_VERSION( DVBSOFTWARECA_VERSION );
