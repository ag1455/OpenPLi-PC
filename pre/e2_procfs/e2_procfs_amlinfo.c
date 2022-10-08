/*
 * e2_procfs_amlinfo.c
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
#include "display/osd/osd_hw.h"
#include <linux/amlogic/vout/vinfo.h>
#include <linux/amlogic/vout/vout_notify.h>
#include <linux/amlogic/ppmgr/ppmgr_status.h>
#include <linux/amlogic/amports/tsync.h>

int e2procfs_amlinfo_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;
	//const vinfo_s *vinfo;
	struct vinfo_s *vinfo;

	vinfo = get_current_vinfo();

	if (proc_info->count > 0)
	{
		 seq_printf(m, "%s", proc_info->bpage);
	}

	seq_printf(m, "name:%s\n", vinfo->name);
	seq_printf(m, "mode:%d\n", vinfo->mode);
	seq_printf(m, "width:%d\n", vinfo->width);
	seq_printf(m, "height:%d\n", vinfo->height);
	seq_printf(m, "field_height:%d\n", vinfo->field_height);
	seq_printf(m, "aspect_ratio_num:%d\n", vinfo->aspect_ratio_num);
	seq_printf(m, "aspect_ratio_den:%d\n", vinfo->aspect_ratio_den);
	seq_printf(m, "sync_duration_num:%d\n", vinfo->sync_duration_num);
	seq_printf(m, "sync_duration_den:%d\n", vinfo->sync_duration_den);
	seq_printf(m, "screen_real_width:%d\n", vinfo->screen_real_width);
	seq_printf(m, "screen_real_height:%d\n", vinfo->screen_real_height);
	seq_printf(m, "video_clk:%d\n", vinfo->video_clk);

	seq_printf(m, "get_use_prot:%d\n", get_use_prot());
	//seq_printf(m, "tsync_get_enable:%d\n", tsync_get_enable());
	seq_printf(m, "tsync_get_mode:%d\n", tsync_get_mode());
	seq_printf(m, "tsync_get_sync_adiscont:%d\n", tsync_get_sync_adiscont());
	seq_printf(m, "tsync_get_sync_vdiscont:%d\n", tsync_get_sync_vdiscont());
	seq_printf(m, "tsync_get_sync_adiscont_diff:%d\n", tsync_get_sync_adiscont_diff());
	seq_printf(m, "tsync_get_sync_vdiscont_diff:%d\n", tsync_get_sync_vdiscont_diff());
	seq_printf(m, "tsync_get_debug_pts_checkin:%d\n", tsync_get_debug_pts_checkin());
	seq_printf(m, "tsync_get_debug_pts_checkout:%d\n", tsync_get_debug_pts_checkout());
	seq_printf(m, "tsync_get_debug_vpts:%d\n", tsync_get_debug_vpts());
	seq_printf(m, "tsync_get_debug_apts:%d\n", tsync_get_debug_apts());
	seq_printf(m, "tsync_get_av_threshold_min:%d\n", tsync_get_av_threshold_min());
	seq_printf(m, "tsync_get_av_threshold_max:%d\n", tsync_get_av_threshold_max());

	return 0;
}

int e2procfs_amlinfo_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_amlosd_show(struct seq_file *m, void* data)
{
	int x, y, w, h;
	int x0, y0, x1, y1;
	//int x_start, y_start, x_end, y_end;
	unsigned int free_scale_enable = 0;
	unsigned int free_scale_mode = 0;
	unsigned int free_scale_width = 0;
	unsigned int free_scale_height = 0;
	//unsigned int osd_antiflicker = 0;

	osd_get_free_scale_enable_hw(0, &free_scale_enable);
	osd_get_free_scale_mode_hw(0, &free_scale_mode);
	seq_printf(m, "osd_get_free_scale_enable:%d\n", free_scale_enable);
	seq_printf(m, "osd_get_free_scale_mode:%d\n", free_scale_mode);

	osd_get_free_scale_width_hw(0, &free_scale_width);
	osd_get_free_scale_height_hw(0, &free_scale_height);
	seq_printf(m, "osd_get_free_scale_width:%d\n", free_scale_width);
	seq_printf(m, "osd_get_free_scale_height:%d\n", free_scale_height);

	osd_get_free_scale_axis_hw(0, &x, &y, &w, &h);
	seq_printf(m, "free_scale_axis:%d %d %d %d\n", x, y, w, h);

	osd_get_scale_axis_hw(0, &x0, &y0, &x1, &y1);
	seq_printf(m, "scale_axis:%d %d %d %d\n", x0, y0, x1, y1);
	osd_get_window_axis_hw(0, &x0, &y0, &x1, &y1);
	seq_printf(m, "window_axis:%d %d %d %d\n", x0, y0, x1, y1);
	//osd_get_osd_antiflicker(0, &osd_antiflicker);
	//seq_printf(m, "osddev_get_osd_antiflicker:%d\n", osd_antiflicker);

	//osd_get_prot_canvas(0, &x_start, &y_start, &x_end, &y_end);
	//seq_printf(m, "prot_canvas:%d %d %d %d\n", x_start, y_start, x_end, y_end);

	seq_printf(m, "gbl_alpha:%d\n", osd_get_gbl_alpha_hw(0));

	return 0;
}

int e2procfs_amlosd_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	u32  gbl_alpha;

	proc_info->bpage = kbuf;

	printk("write alpha: ws=%s", kbuf);

	if (kstrtouint(kbuf, 0, &gbl_alpha))
		return -EINVAL;

	osd_set_gbl_alpha_hw(0, gbl_alpha);

	return 0;
}
