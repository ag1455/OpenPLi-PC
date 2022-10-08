/*
 * e2_procfs_vmpeg.c
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

int e2procfs_vmpeg_dstheight_show(struct seq_file *m, void* data)
{
	struct ProcWriteInfo *proc_info = m->private;
	seq_printf(m, "%08x\n", proc_info->ipage);

	return 0;
}

int e2procfs_vmpeg_dstheight_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
//	int window_height;

	int bytes = 0;
	char buffer[MAX_CHAR_LENGTH];

	bytes = sprintf(buffer, "e2procfs_vmpeg_dstheight_write : %s\n", kbuf);
	save_data_to_file("/tmp/e2procfs_vmpeg_dstheight_write.txt", O_RDWR | O_CREAT | O_APPEND, buffer, bytes);

	proc_info->bpage = kbuf;

/*
	sscanf(kbuf, "%08X", &window_height);

	if (!window_height)
	{
		window_height = 0x240;
	}

	proc_info->ipage = window_height;

    printk("%s()dst_height: %d\n", __FUNCTION__, window_height);
*/

	return 0;
}
