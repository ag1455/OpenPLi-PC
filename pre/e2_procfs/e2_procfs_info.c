/*
 * e2_proc_info.c
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

int e2procfs_info_model_show(struct seq_file *m, void* data)
{
	seq_printf(m, "PC\n");

	return 0;
}

int e2procfs_info_brand_show(struct seq_file *m, void* data)
{
	seq_printf(m, "e2pc\n");

	return 0;
}

int e2procfs_info_chipset_show(struct seq_file *m, void* data)
{
	seq_printf(m, "OpenPLi\n");

	return 0;
}
