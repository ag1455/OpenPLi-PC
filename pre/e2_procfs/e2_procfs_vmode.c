/*
 * e2_procfs_vmode.c
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

int e2procfs_valpha_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s", proc_info->bpage);
	}
	else
	{
		seq_printf(m, "\n");
	}

	return 0;
}

int e2procfs_valpha_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	u32  gbl_alpha;

	proc_info->bpage = kbuf;

	if (kstrtouint(kbuf, 0, &gbl_alpha))
		return -EINVAL;

//	VC_DISPMANX_ALPHA_T alpha = { DISPMANX_FLAGS_ALPHA_FROM_SOURCE | DISPMANX_FLAGS_ALPHA_FIXED_ALL_PIXELS, gbl_alpha, 0 };
	
	return 0;
}

int e2procfs_vmode_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s", proc_info->bpage);
	}
	else
	{
		seq_printf(m, "\n");
	}

	return 0;
}

int e2procfs_vmode_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}


int e2procfs_vchoices24_show(struct seq_file *m, void* data)
{
	seq_printf(m, "576i 576p 720p24 1080i24 1080p24 2160p24\n");

	return 0;
}

int e2procfs_vchoices50_show(struct seq_file *m, void* data)
{
	seq_printf(m, "576i 576p 720p50 1080i50 1080p50 2160p50\n");

	return 0;
}

int e2procfs_vchoices60_show(struct seq_file *m, void* data)
{
	seq_printf(m, "480i 480p 720p 1080i 1080p 2160p\n");

	return 0;
}

int e2procfs_vmode24_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s", proc_info->bpage);
	}
	else
	{
		seq_printf(m, "\n");
	}

	return 0;
}

int e2procfs_vmode24_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_vmode50_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s", proc_info->bpage);
	}
	else
	{
		seq_printf(m, "\n");
	}

	return 0;
}

int e2procfs_vmode50_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_vmode60_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s", proc_info->bpage);
	}
	else
	{
		seq_printf(m, "\n");
	}

	return 0;
}

int e2procfs_vmode60_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_vpchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "bestfit letterbox panscan nonlinear\n");

	return 0;
}

int e2procfs_vpolicy_show(struct seq_file *m, void* data)
{
	seq_printf(m, "panscan\n");

	return 0;
}

int e2procfs_vachoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "any 4:3 16:9 16:10\n");

	return 0;
}
/*
int e2procfs_vaspect_show(struct seq_file *m, void* data)
{
	const struct vinfo_s *vinfo;

	vinfo = get_current_vinfo();

	seq_printf(
		m,
		"%d:%d\n",
		vinfo->aspect_ratio_num,
		vinfo->aspect_ratio_den
	);

	return 0;
}
*/
int e2procfs_vpreferred_show(struct seq_file *m, void* data)
{
	seq_printf(m, "576i 576p 720p50 1080i50 1080p50 2160p50\n");

	return 0;
}

int e2procfs_vchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "576i 576p 720p50 1080i50 1080p50 2160p50\n");

	return 0;
}
