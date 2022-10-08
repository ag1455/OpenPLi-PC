/*
 * e2_procfs_bus.c
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

#include <media/dvb_frontend.h>
#include <media/dvbdev.h>

#define DVB_MAX_FRONTEND 8

enum dvbv3_emulation_type {
	DVBV3_UNKNOWN,
	DVBV3_QPSK,
	DVBV3_QAM,
	DVBV3_OFDM,
	DVBV3_ATSC,
};

static enum dvbv3_emulation_type dvbv3_type(u32 delivery_system)
{
	switch (delivery_system) {
	case SYS_DVBC_ANNEX_A:
	case SYS_DVBC_ANNEX_C:
		return DVBV3_QAM;
	case SYS_DVBS:
	case SYS_DVBS2:
	case SYS_TURBO:
	case SYS_ISDBS:
	case SYS_DSS:
		return DVBV3_QPSK;
	case SYS_DVBT:
	case SYS_DVBT2:
	case SYS_ISDBT:
	case SYS_DTMB:
		return DVBV3_OFDM;
	case SYS_ATSC:
	case SYS_ATSCMH:
	case SYS_DVBC_ANNEX_B:
		return DVBV3_ATSC;
	case SYS_UNDEFINED:
	case SYS_ISDBC:
	case SYS_DVBH:
	case SYS_DAB:
	default:
		/*
		 * Doesn't know how to emulate those types and/or
		 * there's no frontend driver from this type yet
		 * with some emulation code, so, we're not sure yet how
		 * to handle them, or they're not compatible with a DVBv3 call.
		 */
		return DVBV3_UNKNOWN;
	}
}

int e2procfs_nim_sockets_write(struct ProcWriteInfo *proc_info, char *kbuf)
{
	proc_info->bpage = kbuf;

	return 0;
}

int e2procfs_nim_sockets_show(struct seq_file *m, void* data)
{
	int userspace = 0;
	struct ProcWriteInfo *proc_info = m->private;
	char *ArrayDVBTunerType[] =  { "DVB-S","DVB-C","DVB-T","ATSC"};
	char **DVBTunerType;
	DVBTunerType = ArrayDVBTunerType;
/* DVB-S2 is a special case of DVB-S and is tested from frontend capabilities */

	if (proc_info->count > 0)
	{
		seq_printf(m, "%s\n", proc_info->bpage);
	}
	else
	{
 		struct file* fe_fd = NULL;
 		int adapter_num = 0, nsocket_index = 0;
 		char devstr[MAX_CHAR_LENGTH];

/*	User Space nim_socket  (not enabled by default) */
		if ( 	userspace == 1) {
			seq_printf(m,
			"NIM Socket 0:\n"
			"\tType: DVB-T2\n"
			"\tName: Generic Card\n"
			"\tHas_Outputs: no\n"
			"\tFrontend_Device: 0\n"
			);
		}
		else	{
			while (adapter_num < DVB_MAX_ADAPTERS)
			{
				int frontend_num = 0;

	 			while (frontend_num < DVB_MAX_FRONTEND)
				{
					int bytes = 0;

					bytes = sprintf(devstr, "/dev/dvb/adapter%d/frontend%d", adapter_num, frontend_num);

					fe_fd = file_open(devstr, O_RDONLY, bytes);

					if (fe_fd != NULL)
					{
						struct dvb_device *dvbdev = fe_fd->private_data;
						struct dvb_frontend *fe = dvbdev->priv;
						struct dvb_frontend_info fe_info;
						memset(&fe_info, 0, sizeof(fe_info));
						struct dtv_frontend_properties *fe_prop = &fe->dtv_property_cache;

						if (dvb_generic_ioctl(fe_fd, FE_GET_INFO, 0))
						{
							strcpy(fe_info.name, fe->ops.info.name);
							fe_info.caps = fe->ops.info.caps;
							switch (dvbv3_type(fe_prop->delivery_system)) {
								case DVBV3_QPSK:
									fe_info.type = FE_QPSK;
									break;
								case DVBV3_ATSC:
									fe_info.type = FE_ATSC;
									break;
								case DVBV3_QAM:
									fe_info.type = FE_QAM;
									break;
								case DVBV3_OFDM:
									fe_info.type = FE_OFDM;
									break;
								default:
									fe_info.type = FE_OFDM;
							}


/* 2nd generation DVB Tuner detected adding 2 to the TunerType */
								if ( (fe_info.caps & FE_CAN_2G_MODULATION ) == FE_CAN_2G_MODULATION )
								{
									seq_printf(m,
									"NIM Socket %d:\n"
									"\tType: %s2\n"
									"\tName: %s\n"
									"\tHas_Outputs: no\n"
								//	"\tInternally_Connectable: 0\n"
									"\tFrontend_Device: %d\n"
								//	"\tI2C_Device: -1\n"
									,
									nsocket_index,
		 							DVBTunerType[fe_info.type],
									fe_info.name,
									frontend_num
									);
		 						}	
								else	{
									seq_printf(m,
	 								"NIM Socket %d:\n"
									"\tType: %s\n"
	 								"\tName: %s\n"
									"\tHas_Outputs: no\n"
								//	"\tInternally_Connectable: 0\n"
									"\tFrontend_Device: %d\n"
								//	"\tI2C_Device: -1\n"
									,
	 								nsocket_index,
									DVBTunerType[fe_info.type],
									fe_info.name,
									frontend_num
									);
								}

								nsocket_index++;
						}
					}

					frontend_num++;

					file_close(fe_fd);
				}

				adapter_num++;
			}
		}
	}

	return 0;
}
