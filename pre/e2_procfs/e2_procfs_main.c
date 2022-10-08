/*
 * e2_proc_main.c
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

struct ProcStructure_s e2Proc[] =
{
	{cProcEntry, "progress"                                                         , NULL, e2procfs_progress_show, e2procfs_progress_write, NULL, ""},

	{cProcEntry, "bus/nim_sockets"                                                  , NULL, e2procfs_nim_sockets_show, e2procfs_nim_sockets_write, NULL, ""},
	{cProcDir  , "stb"                                                              , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/audio"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/audio/ac3"                                                    , NULL, e2procfs_ac3_show, e2procfs_ac3_write, NULL, ""},
	{cProcEntry, "stb/audio/audio_delay_pcm"                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/audio/audio_delay_bitstream"                                  , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/audio/j1_mute"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/audio/ac3_choices"                                            , NULL, e2procfs_ac3choices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/dts"                                                    , NULL, e2procfs_dts_show, e2procfs_dts_write, NULL, ""},
	{cProcEntry, "stb/audio/dts_choices"                                            , NULL, e2procfs_dtschoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/aac"                                                    , NULL, e2procfs_aac_show, e2procfs_aac_write, NULL, ""},
	{cProcEntry, "stb/audio/aac_choices"                                            , NULL, e2procfs_aacchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/avl"                                                    , NULL, e2procfs_avl_show, e2procfs_avl_write, NULL, ""},
	{cProcEntry, "stb/audio/avl_choices"                                            , NULL, e2procfs_avlchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/autovolumelevel"                                        , NULL, e2procfs_autovolumelevel_show, e2procfs_aac_write, NULL, ""},
	{cProcEntry, "stb/audio/autovolumelevel_choices"                                , NULL, e2procfs_autovolumelevelchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/multichannel_pcm"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/audio/3dsurround"                                             , NULL, e2procfs_3dsurround_show, e2procfs_3dsurround_write, NULL, ""},
	{cProcEntry, "stb/audio/3dsurround_choices"                                     , NULL, e2procfs_3dsurroundchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/3dsurround_softlimiter_choices"                         , NULL, e2procfs_3dsurround_softlimiterchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/3dsurround_softlimiter"                                 , NULL, e2procfs_3dsurround_softlimiter_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/3d_surround"                                            , NULL, e2procfs_3d_surround_show, e2procfs_3d_surround_write, NULL, ""},
	{cProcEntry, "stb/audio/3d_surround_choices"                                    , NULL, e2procfs_3d_surroundchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/3d_surround_speaker_position"                           , NULL, e2procfs_3d_surround_speaker_position_show, NULL, NULL, ""},
	{cProcEntry, "stb/audio/3d_surround_speaker_position_choices"                   , NULL, e2procfs_3d_surround_speaker_positionchoices_show, NULL, NULL, ""},

	{cProcDir  , "stb/frontend"                                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/dvr_source_offset"                                   , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/frontend/0"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/mode"                                              , NULL, e2procfs_frontend_mode_show, e2procfs_frontend_mode_write, NULL, ""},
	{cProcEntry, "stb/frontend/0/t2mi"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/t2mirawmode"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/lnb_sense"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/static_current_limiting"                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/active_antenna_power"                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/rf_switch"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/use_scpc_optimized_search_range"                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/tone_amplitude"                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/0/fbc_id"                                            , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/frontend/1"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/mode"                                              , NULL, e2procfs_frontend_mode_show, e2procfs_frontend_mode_write, NULL, ""},
	{cProcEntry, "stb/frontend/1/t2mi"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/t2mirawmode"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/lnb_sense"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/static_current_limiting"                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/active_antenna_power"                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/rf_switch"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/use_scpc_optimized_search_range"                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/tone_amplitude"                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/frontend/1/fbc_id"                                            , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/info"                                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/info/boxtype"                                                 , NULL, e2procfs_info_model_show, NULL, NULL, ""},
	{cProcEntry, "stb/info/chipset"                                                 , NULL, e2procfs_info_chipset_show, NULL, NULL, ""},
	{cProcEntry, "stb/info/vumodel"                                                 , NULL, e2procfs_info_model_show, NULL, NULL, ""},
	{cProcEntry, "stb/info/version"                                                 , NULL, e2procfs_info_chipset_show, NULL, NULL, ""},
	{cProcEntry, "stb/info/board_revision"                                          , NULL, e2procfs_info_brand_show, NULL, NULL, ""},
	{cProcEntry, "stb/info/brandname"                                               , NULL, e2procfs_info_brand_show, NULL, NULL, ""},

	{cProcDir  , "stb/video"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/alpha"                                                  , NULL, e2procfs_valpha_show, e2procfs_valpha_write, NULL, ""},
	{cProcEntry, "stb/video/aspect"                                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/aspect_choices"                                         , NULL, e2procfs_vachoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/policy"                                                 , NULL, e2procfs_vpolicy_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/policy_choices"                                         , NULL, e2procfs_vpchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/videomode"                                              , NULL, e2procfs_vmode_show, e2procfs_vmode_write, NULL, ""},
	{cProcEntry, "stb/video/videomode_24hz"                                         , NULL, e2procfs_vmode24_show, e2procfs_vmode24_write, NULL, ""},
	{cProcEntry, "stb/video/videomode_50hz"                                         , NULL, e2procfs_vmode50_show, e2procfs_vmode50_write, NULL, ""},
	{cProcEntry, "stb/video/videomode_60hz"                                         , NULL, e2procfs_vmode60_show, e2procfs_vmode60_write, NULL, ""},
	{cProcEntry, "stb/video/videomode_24hz_choices"                                 , NULL, e2procfs_vchoices24_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/videomode_50hz_choices"                                 , NULL, e2procfs_vchoices50_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/videomode_60hz_choices"                                 , NULL, e2procfs_vchoices60_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/videomode_preferred"                                    , NULL, e2procfs_vpreferred_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/videomode_choices"                                      , NULL, e2procfs_vchoices_show, NULL, NULL, ""},
	{cProcEntry, "stb/video/zapmode"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/hdmi_colorspace"                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/hdmi_colordepth"                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/hdmi_hdrtype"                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/disable_12bit"                                          , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/video/disable_10bit"                                          , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/avs"                                                          , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/avs/0"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/avs/0/colorformat"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/avs/0/fb"                                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/avs/0/input"                                                  , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/avs/0/volume"                                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/avs/0/input_choices"                                          , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/denc"                                                         , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/denc/0"                                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/denc/0/wss"                                                   , NULL, e2procfs_wss_denc_show, e2procfs_wss_denc_write, NULL, ""},

	{cProcDir  , "stb/fb"                                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/3dmode"                                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/znorm"                                                     , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/fb/primary"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/primary/zoffset"                                           , NULL, NULL, NULL, NULL, ""},
//	{cProcEntry, "stb/fb/sd_detach"                                                 , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/fp"                                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/version"                                                   , NULL, e2procfs_fpver_show, NULL, NULL, ""},
	{cProcEntry, "stb/fp/events"                                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/temp_sensor_avs"                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/temp_sensor"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/vcr_fns"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/vcr_fns failed"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/dst_left"                                                  , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/dst_width"                                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/dst_height"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fb/dst_top"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/fan_vlt"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/fan"                                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/fan_speed"                                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/fan_pwm"                                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/led0_pattern"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/led_pattern_speed"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/led_set_pattern"                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/led_set_speed"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/rtc_offset"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/rtc failed"                                                , NULL, NULL, NULL, NULL, ""},
/*	{cProcEntry, "stb/fp/ledpowercolor"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/ledstandbycolor"                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/ledsuspendledcolor"                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/power4x7on"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/power4x7standby"                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/fp/power4x7suspend"                                           , NULL, NULL, NULL, NULL, ""},
	//rtc is disabled for now because it causes segmentation fault
	{cProcEntry, "stb/fp/wakeup_time"                                               , NULL, e2procfs_fpwut_show, e2procfs_fpwut_write, NULL, ""},
	{cProcEntry, "stb/fp/was_timer_wakeup"                                          , NULL, e2procfs_fpwtw_show, e2procfs_fpwtw_write, NULL, ""},
	{cProcEntry, "stb/fp/rtc"                                                       , NULL, e2procfs_fprtc_show, e2procfs_fprtc_write, NULL, ""},*/

	{cProcDir  , "stb/tsmux"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/tsmux/input"                                                  , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/tsmux/input0"                                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/tsmux/input1"                                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/tsmux/ci0_input"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/tsmux/ci0_input_choices"                                      , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/misc"                                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/misc/12V_output"                                              , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/vmpeg"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/vmpeg/0"                                                      , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/dst_left"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/dst_top"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/dst_width"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/dst_height"                                           , NULL, NULL, e2procfs_vmpeg_dstheight_write, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/aspect"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/framerate"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/progressive"                                          , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_scaler_sharpness"                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_apply"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_contrast"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_saturation"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_hue"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_brightness"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_block_noise_reduction"                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_mosquito_noise_reduction"                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_digital_contour_removal"                          , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_split"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_sharpness"                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_auto_flesh"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_green_boost"                                      , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_blue_boost"                                       , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_dynamic_contrast"                                 , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/pep_scaler_vertical_dejagging"                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/gamma"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/0/dst_"                                                 , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/vmpeg/1"                                                      , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/1/external"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/1/visible"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/1/gamma"                                                , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/vmpeg/1/dst_"                                                 , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/hdmi"                                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/hdmi/bypass_edid_checking"                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/hdmi/audio_source"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/hdmi/preemphasis"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/hdmi/hlg_support_choices"                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/hdmi/hdr10_support"                                           , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/encoder"                                                      , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/decoder"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/bitrate"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/width"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/height"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/display_format"                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/framerate"                                          , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/interlaced"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/aspectratio"                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/apply"                                              , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/encoder/0/vcodec_choices"                                     , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/lcd"                                                          , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/mode"                                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/oled_brightness"                                          , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/oled_brightness failed"                                   , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/xres"                                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/yres"                                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/live_decoder"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/bpp"                                                      , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/symbol_circle"                                            , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/symbol_recording"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/symbol_timeshift"                                         , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/symbol_hdd"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/show_symbols"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/scroll_repeats"                                           , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/scroll_delay"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/initial_scroll_delay"                                     , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/lcd/final_scroll_delay"                                       , NULL, NULL, NULL, NULL, ""},
//	{cProcEntry, "stb/lcd/live_enable"                                              , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/power"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/power/avs"                                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/power/powerled"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/power/standbyled"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/power/suspendled"                                             , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/power/vfd"                                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/power/wol"                                                    , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/sensors"                                                      , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/sensors/0"                                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/sensors/0/name"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/sensors/0/unit"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/sensors/1"                                                    , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/sensors/1/name"                                               , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/sensors/1/unit"                                               , NULL, NULL, NULL, NULL, ""},

	{cProcDir  , "stb/ir"                                                           , NULL, NULL, NULL, NULL, ""},
	{cProcDir  , "stb/ir/rc"                                                        , NULL, NULL, NULL, NULL, ""},
	{cProcEntry, "stb/ir/rc/type"                                                   , NULL, NULL, NULL, NULL, ""},
};

struct proc_dir_entry * find_proc_dir(char * name)
{
	int i;

	for (i = 0; i < sizeof(e2Proc) / sizeof(e2Proc[0]); i++)
	{
		if ((e2Proc[i].type == cProcDir) && (strcmp(name, e2Proc[i].name) == 0))
			return e2Proc[i].entry;
	}

	return NULL;
}

static int e2procfs_show(struct seq_file *m, void* data)
{
	int bytes = 0;
	char bufferfile[MAX_CHAR_LENGTH];
	struct ProcWriteInfo *proc_info = m->private;
	seq_printf(m, "\n");

	bytes = sprintf(bufferfile, "e2procfs_show : proc_info->proc_i = %d\n", proc_info->proc_i);
	save_data_to_file("/tmp/e2procfs_show.txt", O_RDWR | O_CREAT | O_APPEND, bufferfile, bytes);

	return 0;
}

static int e2procfs_open(struct inode *inode, struct file *file)
{
	struct ProcWriteInfo *proc_info;
	int i;
	char *path, *ptr = NULL, *e2Proc_fpath = NULL;

	proc_info = kmalloc(sizeof(struct ProcWriteInfo), GFP_KERNEL);
	if (proc_info == NULL)
		return -ENOMEM;

	path = kmalloc(PAGE_SIZE, GFP_KERNEL);
	e2Proc_fpath = kmalloc(PAGE_SIZE, GFP_KERNEL);
	ptr = d_path(&file->f_path, path, PAGE_SIZE);

	proc_info->proc_i = -EPERM;

	for (i = 0; i < sizeof(e2Proc) / sizeof(e2Proc[0]); i++)
	{
		int bytes = 0;
		char buffer[MAX_CHAR_LENGTH];

		sprintf(e2Proc_fpath, "/proc/%s", e2Proc[i].name);

		bytes = sprintf(buffer, "e2Proc : file->f_mode = %d / %s / %s == %s\n", file->f_mode, e2Proc[i].name, ptr, e2Proc_fpath);
//		save_data_to_file("/tmp/e2Proc.txt", O_RDWR | O_CREAT | O_APPEND, buffer, bytes);

//		if (e2Proc[i].type == cProcEntry && strstr(ptr, e2Proc[i].name))
		if (e2Proc[i].type == cProcEntry && !strcmp(ptr, e2Proc_fpath))
		{
			proc_info->proc_i = i;
			proc_info->count = -EPERM;

			if (file->f_mode & FMODE_READ)
			{
				if (e2Proc[i].read_proc != NULL)
				{
					if (e2Proc[i].proc_info != NULL)
					{
						proc_info = e2Proc[i].proc_info;
					}

					return single_open(file, e2Proc[i].read_proc, proc_info);
				}

				return single_open(file, e2procfs_show, proc_info);
			}
			else if (file->f_mode & FMODE_WRITE)
			{
				if (e2Proc[i].write_proc == NULL)
				{
					proc_info->proc_i = -EPERM;
				}

				file->private_data = proc_info;
			}

			break;
		}
	}

	return 0;
}

static ssize_t e2procfs_write(struct file *file, const char __user *ubuf, size_t count, loff_t *ppos)
{
	struct ProcWriteInfo *proc_info = file->private_data;
	char *kbuf;

	kbuf = kmalloc(count + 1, GFP_KERNEL);
	if (!kbuf)
		return -ENOMEM;

	if (copy_from_user(kbuf, ubuf, count)) {
		count = -EFAULT;
	}
	else
	{
		kbuf[count] = '\0'; /* Just to make sure... */

		if (proc_info->proc_i >= 0)
		{
			int proc_i = proc_info->proc_i;

			proc_info->ubuf = ubuf;
			proc_info->count = count;
			e2Proc[proc_i].write_proc(proc_info, kbuf);
			e2Proc[proc_i].proc_info = proc_info;
		}
	}

	return count;
}

static unsigned int e2procfs_poll(struct file *file, struct poll_table_struct *wait)
{
	unsigned int mask = 0;

#ifdef DEBUG
	printk(KERN_DEBUG "e2procfs: poll called (unimplemented)\n");
#endif

	return mask;
}

static int e2procfs_release(struct inode *inode, struct file *file)
{
//	struct ProcWriteInfo *proc_info = file->private_data;

#ifdef DEBUG
	printk(KERN_DEBUG "e2procfs: release called\n");
#endif
//	kfree(proc_info);

	return 0;
}
#if LINUX_VERSION_CODE >= KERNEL_VERSION(5,6,0)
static const struct proc_ops e2procfs_fops = {
	.proc_open	= e2procfs_open,
	.proc_read	= seq_read,
	.proc_write	= e2procfs_write,
	.proc_lseek	= no_llseek,
	.proc_poll	= e2procfs_poll,
	.proc_mmap	= NULL,
	.proc_release	= e2procfs_release,
};
#else
static const struct file_operations e2procfs_fops = {
	.owner          = THIS_MODULE,
	.open           = e2procfs_open,
	.read           = seq_read,
	.write          = e2procfs_write,
	.llseek         = no_llseek,
	.poll           = e2procfs_poll,
	.mmap           = NULL,
	.release        = e2procfs_release,
};
#endif
static int __init e2procfs_init_module(void)
{
	int i;
	char *path;
	char *name;

	for (i = 0; i < sizeof(e2Proc) / sizeof(e2Proc[0]); i++)
	{
		path = dirname(e2Proc[i].name);
		name = basename(e2Proc[i].name);

		switch (e2Proc[i].type)
		{
			case cProcDir:
				e2Proc[i].entry = proc_mkdir(name, find_proc_dir(path));

				if (e2Proc[i].entry == NULL)
				{
					printk("%s(): could not create entry %s\n", __func__, e2Proc[i].name);
				}

				break;
			case cProcEntry:
				e2Proc[i].entry = proc_create(
					(strcmp("bus", path) == 0) ? e2Proc[i].name : name,
					0,
					(strcmp("bus", path) == 0) ? NULL : find_proc_dir(path),
					&e2procfs_fops
				);

				break;
			default:
				printk("%s(): invalid type %d\n", __func__, e2Proc[i].type);
		}
	}

	return 0;
}

static void __exit e2procfs_cleanup_module(void)
{
	int i;
	int bytes = 0;
	char buffer[MAX_CHAR_LENGTH];

	for (i = sizeof(e2Proc) / sizeof(e2Proc[0]) - 1; i >= 0; i--)
	{
		remove_proc_entry(e2Proc[i].name, NULL);

		bytes = sprintf(buffer, "remove_proc_entry : %s\n", e2Proc[i].name);
	//	save_data_to_file("/tmp/kernel.txt", O_RDWR | O_CREAT | O_APPEND, buffer, bytes);
	}
}
MODULE_AUTHOR("Open Vision developers");
MODULE_DESCRIPTION("e2pc procfs driver");
MODULE_LICENSE("GPL");
MODULE_VERSION("1.0.0");
module_init(e2procfs_init_module);
module_exit(e2procfs_cleanup_module);
