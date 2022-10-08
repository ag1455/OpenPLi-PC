/*
 * e2_procfs.h
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

/*
 * Description:
 *
 * progress
 *  |
 * bus
 *  |
 *  ----------- nim_sockets
 *  |
 * stb
 *  |
 *  ----------- audio
 *  |             |
 *  |             --------- ac3
 *  |             |
 *  |             --------- audio_delay_pcm
 *  |             |
 *  |             --------- audio_delay_bitstream
 *  |             |
 *  |             --------- audio_j1_mute
 *  |             |
 *  |             --------- ac3_choices
 *  |             |
 *  |             ---------
 *  |
 *  ----------- video
 *  |             |
 *  |             --------- alpha
 *  |             |
 *  |             --------- aspect
 *  |             |
 *  |             --------- aspect_choices
 *  |             |
 *  |             --------- force_dvi
 *  |             |
 *  |             --------- policy
 *  |             |
 *  |             --------- policy_choices
 *  |             |
 *  |             --------- videomode
 *  |             |
 *  |             --------- videomode_50hz
 *  |             |
 *  |             --------- videomode_60hz
 *  |             |
 *  |             --------- videomode_choices
 *  |             |
 *  |             --------- videomode_preferred
 *  |             |
 *  |             --------- pal_v_start
 *  |             |
 *  |             --------- pal_v_end
 *  |             |
 *  |             --------- pal_h_start
 *  |             |
 *  |             --------- pal_h_end
 *  |
 *  ---------- avs
 *  |           |
 *  |           --------- 0
 *  |               |
 *  |               --------- colorformat <-colorformat in generlell, hdmi and scart
 *  |               |
 *  |               --------- colorformat_choices
 *  |               |
 *  |               --------- fb <-fastblanking
 *  |               |
 *  |               --------- sb <-slowblanking
 *  |               |
 *  |               --------- volume
 *  |               |
 *  |               --------- input  <-Input, Scart VCR Input or Encoder
 *  |               |
 *  |               --------- input_choices
 *  |               |
 *  |               --------- standby
 *  |
 *  ---------- denc
 *  |           |
 *  |           --------- 0
 *  |               |
 *  |               --------- wss
 *  |               |
 *  |               ---------
 *  |               |
 *  |               ---------
 *  |
 *  ---------- fp (this is wrong used for e2 I think. on dm800 this is frontprocessor and there is another proc entry for frontend)
 *  |           |
 *  |           --------- lnb_sense1
 *  |           |
 *  |           --------- lnb_sense2
 *  |           |
 *  |           --------- led0_pattern
 *  |           |
 *  |           --------- led_pattern_speed
 *  |           |
 *  |           |
 *  |           --------- version
 *  |           |
 *  |           --------- wakeup_time <- dbox frontpanel wakeuptime
 *  |           |
 *  |           --------- was_timer_wakeup
 *  |
 *  |
 *  ---------- hdmi
 *  |           |
 *  |           --------- bypass_edid_checking
 *  |           |
 *  |           --------- enable_hdmi_resets
 *  |           |
 *  |           --------- audio_source
 *  |           |
 *  |           ---------
 *  |
 *  ---------- info
 *  |           |
 *  |           --------- model <- Version String of out Box
 *  |
 *  ---------- tsmux
 *  |           |
 *  |           --------- input0
 *  |           |
 *  |           --------- input1
 *  |           |
 *  |           --------- ci0_input
 *  |           |
 *  |           --------- ci1_input
 *  |           |
 *  |           --------- lnb_b_input
 *  |           |
 *  |           ---------
 *  |
 *  ---------- misc
 *  |           |
 *  |           --------- 12V_output
 *  |
 *  ---------- tuner (dagoberts tuner entry ;-) )
 *  |           |
 *  |           ---------
 *  |
 *  ---------- vmpeg
 *  |           |
 *  |           --------- 0/1
 *  |               |
 *  |               --------- dst_left   \
 *  |               |                     |
 *  |               --------- dst_top     |
 *  |               |                      >  PIG WINDOW SIZE AND POSITION
 *  |               --------- dst_width   |
 *  |               |                     |
 *  |               --------- dst_height /
 *  |               |
 *  |               --------- dst_all (Dagobert: Dont confuse player by setting value one after each other)
 *  |
 *  |               |TODO
 *  |               | v
 *  |               --------- yres
 *  |               |
 *  |               --------- xres
 *  |               |
 *  |               --------- framerate
 *  |               |
 *  |               --------- progressive
 *  |               |
 *  |               --------- aspect
 *
 */

#ifndef H_E2_PROCFS
#define H_E2_PROCFS

#include <linux/version.h>
#include <linux/string.h>
#include <linux/module.h>

#include <linux/slab.h>
#include <linux/namei.h>
#include <linux/seq_file.h>
#include <linux/proc_fs.h>
#include <linux/delay.h>
#include <linux/uaccess.h>
#include <linux/platform_device.h>


//extern int rtc_set_alarm_aml(struct device *dev,struct alarm_data_s *alarm_data);

#define MAX_CHAR_LENGTH 256
#define cProcDir	1
#define cProcEntry	2

struct ProcWriteInfo
{
	int					proc_i;
	int					count;
	int					ipage;
	char				*bpage;
	const char __user	*ubuf;
};

typedef int (*proc_read_t) (struct seq_file *m, void* data);
typedef int (*proc_write_t_e2) (struct ProcWriteInfo *proc_info, char *kbuf);

struct ProcStructure_s
{
	int						type;
	char*					name;
	struct proc_dir_entry*	entry;
	proc_read_t				read_proc;
	proc_write_t_e2			write_proc;
	struct ProcWriteInfo*	proc_info;
	void*					identifier; /* needed for cpp stuff */
};

struct file* file_open(const char* path, int flags, int rights);
void file_close(struct file* file);
int file_read(struct file* file, unsigned char* data, unsigned int size);
int file_write(struct file* file, unsigned char* data, unsigned int size);
int remove_file(char *path);
int save_data_to_file(char *path, int flags, char *data, int size);
char * dirname(char * name);
char * basename(char * name);

int e2procfs_ac3_show(struct seq_file *m, void* data);
int e2procfs_ac3_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_ac3choices_show(struct seq_file *m, void* data);
int e2procfs_dts_show(struct seq_file *m, void* data);
int e2procfs_dts_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_dtschoices_show(struct seq_file *m, void* data);
int e2procfs_aac_show(struct seq_file *m, void* data);
int e2procfs_aac_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_aacchoices_show(struct seq_file *m, void* data);
int e2procfs_avl_show(struct seq_file *m, void* data);
int e2procfs_avl_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_avlchoices_show(struct seq_file *m, void* data);
int e2procfs_3dsurround_show(struct seq_file *m, void* data);
int e2procfs_3dsurround_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_3dsurroundchoices_show(struct seq_file *m, void* data);
int e2procfs_3dsurround_softlimiter_show(struct seq_file *m, void* data);
int e2procfs_3dsurround_softlimiterchoices_show(struct seq_file *m, void* data);
int e2procfs_3d_surround_show(struct seq_file *m, void* data);
int e2procfs_3d_surround_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_3d_surroundchoices_show(struct seq_file *m, void* data);
int e2procfs_3d_surround_speaker_position_show(struct seq_file *m, void* data);
int e2procfs_3d_surround_speaker_positionchoices_show(struct seq_file *m, void* data);
int e2procfs_autovolumelevel_show(struct seq_file *m, void* data);
int e2procfs_autovolumelevel_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_autovolumelevelchoices_show(struct seq_file *m, void* data);

int e2procfs_info_model_show(struct seq_file *m, void* data);
int e2procfs_info_brand_show(struct seq_file *m, void* data);
int e2procfs_info_chipset_show(struct seq_file *m, void* data);
int e2procfs_nim_sockets_show(struct seq_file *m, void* data);

int e2procfs_progress_show(struct seq_file *m, void* data);
int e2procfs_progress_write(struct ProcWriteInfo *proc_info, char *kbuf);

int e2procfs_valpha_show(struct seq_file *m, void* data);
int e2procfs_valpha_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_vmode_show(struct seq_file *m, void* data);
int e2procfs_vmode_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_vchoices24_show(struct seq_file *m, void* data);
int e2procfs_vchoices50_show(struct seq_file *m, void* data);
int e2procfs_vchoices60_show(struct seq_file *m, void* data);
int e2procfs_vmode24_show(struct seq_file *m, void* data);
int e2procfs_vmode24_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_vmode50_show(struct seq_file *m, void* data);
int e2procfs_vmode50_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_vmode60_show(struct seq_file *m, void* data);
int e2procfs_vmode60_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_vpchoices_show(struct seq_file *m, void* data);
int e2procfs_vpolicy_show(struct seq_file *m, void* data);
int e2procfs_vachoices_show(struct seq_file *m, void* data);
int e2procfs_vaspect_show(struct seq_file *m, void* data);
int e2procfs_vpreferred_show(struct seq_file *m, void* data);
int e2procfs_vchoices_show(struct seq_file *m, void* data);

int e2procfs_fpver_show(struct seq_file *m, void* data);
int e2procfs_fprtc_show(struct seq_file *m, void* data);
int e2procfs_fprtc_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_fpwut_show(struct seq_file *m, void* data);
int e2procfs_fpwut_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_fpwtw_show(struct seq_file *m, void* data);
int e2procfs_fpwtw_write(struct ProcWriteInfo *proc_info, char *kbuf);

int e2procfs_wss_denc_show(struct seq_file *m, void* data);
int e2procfs_wss_denc_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_wssc_denc_show(struct seq_file *m, void* data);

int e2procfs_amlinfo_show(struct seq_file *m, void* data);
int e2procfs_amlinfo_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_amlosd_show(struct seq_file *m, void* data);
int e2procfs_amlosd_write(struct ProcWriteInfo *proc_info, char *kbuf);

int e2procfs_vmpeg_dstheight_show(struct seq_file *m, void* data);
int e2procfs_vmpeg_dstheight_write(struct ProcWriteInfo *proc_info, char *kbuf);

int e2procfs_frontend_mode_show(struct seq_file *m, void* data);
int e2procfs_frontend_mode_write(struct ProcWriteInfo *proc_info, char *kbuf);
int e2procfs_nim_sockets_write(struct ProcWriteInfo *proc_info, char *kbuf);

#endif
