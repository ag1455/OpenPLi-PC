/*
 * e2_procfs_fp.c
 *
 * (c) 2015 SIP-Online
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 */

#include "e2_procfs.h"
#include <linux/platform_device.h>
/*
#include <linux/amlogic/aml_rtc.h>

#define RTC_GPO_COUNTER_ADDR		1

 struct alarm_data_s {
	int level;
	unsigned alarm_sec;   //in s
} alarm_data_t;

unsigned int ser_access_read(unsigned long addr);
int ser_access_write(unsigned long addr, unsigned long data);
int rtc_set_alarm_aml(struct device *dev, struct alarm_data_s *alarm_data);
*/
int e2procfs_fpver_show(struct seq_file *m, void* data)
{
	seq_printf(m, "1\n");

	return 0;
}
/*
int e2procfs_fprtc_show(struct seq_file *m, void* data)
{
	unsigned int sa_read;

	sa_read = ser_access_read(0);
	seq_printf(m, "%u", sa_read);

	return 0;
}

int e2procfs_fprtc_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	struct timespec tv;
	unsigned long  data = 0x500000;

	proc_info->bpage = kbuf;

	if (kstrtoul_from_user(proc_info->ubuf, proc_info->count, 0, &tv.tv_nsec))
		return -EINVAL;

	ser_access_write(RTC_GPO_COUNTER_ADDR, data);
	do_settimeofday(&tv);

	return 0;
}

int e2procfs_fpwut_show(struct seq_file *m, void* data)
{
	unsigned int armr_read;

	armr_read = aml_read_rtc_mem_reg(0);
	seq_printf(m, "%u", armr_read);

	return 0;
}

int e2procfs_fpwut_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	struct alarm_data_s alarm_data;
	unsigned long wut, v8;
	unsigned int sa_read;

	proc_info->bpage = kbuf;

	sa_read = ser_access_read(0);

	if (kstrtoul_from_user(proc_info->ubuf, proc_info->count, 0, &wut))
		return -EINVAL;

	if (wut <= sa_read)
    {
		printk("[FP_RTC] Wrong wakeup time %ld < %u!\n", wut, sa_read);
    }
    else
    {
		v8 = wut - sa_read;

		if (!rtc_set_alarm_aml(0, &alarm_data))
		{
			aml_write_rtc_mem_reg(0, wut);
			aml_write_rtc_mem_reg(1, 1);
		}
	}

	return 0;
}

int e2procfs_fpwtw_show(struct seq_file *m, void* data)
{
	unsigned int armr_read;

	armr_read = aml_read_rtc_mem_reg(1);
	seq_printf(m, "%u", armr_read);

	return 0;
}

int e2procfs_fpwtw_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	unsigned long wtw;

	proc_info->bpage = kbuf;

	if (kstrtoul_from_user(proc_info->ubuf, proc_info->count, 0, &wtw))
		return -EINVAL;

	aml_write_rtc_mem_reg(1, wtw);

	return 0;
}
*/
