/*
 * e2_procfs_denc.c
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

int e2procfs_wss_denc_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s", proc_info->bpage);
	}
	else
	{
		seq_printf(m, "auto\n");
	}

	return 0;
}

int e2procfs_wss_denc_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_wssc_denc_show(struct seq_file *m, void* data)
{
	seq_printf(m, "auto\n");

	return 0;
}
