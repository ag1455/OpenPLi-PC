/*
 * e2_procfs_amode.c
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

int e2procfs_ac3_show(struct seq_file *m, void* data)
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

int e2procfs_ac3_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_ac3choices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "downmix passthrough\n");

	return 0;
}

int e2procfs_dts_show(struct seq_file *m, void* data)
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

int e2procfs_dts_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_dtschoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "downmix passthrough\n");

	return 0;
}

int e2procfs_aac_show(struct seq_file *m, void* data)
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

int e2procfs_aac_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_aacchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "downmix passthrough\n");

	return 0;
}

int e2procfs_avl_show(struct seq_file *m, void* data)
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

int e2procfs_avl_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_avlchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "downmix passthrough\n");

	return 0;
}

int e2procfs_3dsurround_show(struct seq_file *m, void* data)
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

int e2procfs_3dsurround_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_3dsurroundchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "downmix passthrough\n");

	return 0;
}

int e2procfs_3dsurround_softlimiter_show(struct seq_file *m, void* data)
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

int e2procfs_3dsurround_softlimiterchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "enabled disabled\n");

	return 0;
}

int e2procfs_3d_surround_show(struct seq_file *m, void* data)
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

int e2procfs_3d_surround_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_3d_surroundchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "enabled disabled\n");

	return 0;
}

int e2procfs_3d_surround_speaker_position_show(struct seq_file *m, void* data)
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

int e2procfs_3d_surround_speaker_positionchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "front rear center left right\n");

	return 0;
}

int e2procfs_autovolumelevel_show(struct seq_file *m, void* data)
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

int e2procfs_autovolumelevel_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_autovolumelevelchoices_show(struct seq_file *m, void* data)
{
	seq_printf(m, "enabled disabled\n");

	return 0;
}
