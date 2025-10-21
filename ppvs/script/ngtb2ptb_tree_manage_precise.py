#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Describe: Create PVTB Tree, NGTB2PVTB
@Author: Guo Shihao
Data: 2025.08.30
"""

import os, re, sys, time, stat, pdb, shutil, argparse, pexpect, getpass, subprocess
from pathlib import Path
from collections import defaultdict
cdir = os.path.dirname(os.path.realpath(__file__)) + '/'

class PVTBTree():
    def __init__(self):
        self.i, self.j = 2, 2 # one iteration is enough
        self.project = 'src' #'archpv_saipan'
        self.shell_list = ['cpc', 'cpf', 'rlc', 'cpg', 'bpmh', 'gc_internal_monitors', 'core_dumpctrl', 'send_signal_monitor', 'core_trackers', 'power_ip', 'dbgu_gfx', 'gc_cac', 'rdft_se_wrapper', 'tpi', 'gfx_dbg_steer_wrapper', 'gfx_dbg_client_oring', 'cpaxi', 'cci' ] #, 'gds' 'sq_monitors','gc', 'cp', rdft_gc_wrapper
        self.shell_sub_module_list = ['ccim', 'cci', 'cpc_save', 'cpc_mec', 'cpg', 'gc_internal_monitors', 'power_ip', 'core_dumpctrl', 'send_signal_monitor'] #, 'core_trackers', 'sq_monitors', 'power_ip' ] # can not have some module, because will use these sub-module: bpmh, cp, gc, rlc, cpf, 'gds', 
        self.cmt_sv_list = ['rlc.vu.sv', 'cpf.vu.sv', 'cpc.vu.sv', 'cpg.vu.sv'] #, 'sq_monitors_se_sh_cu.sv'
        self.cmt_specific_list = ['sdp_if.sv', 'sdp_uvc_pkg.sv', 'sdp_uvc_dpi_pkg.sv', 'amd_axi4_uvc_pkg.sv', 'amd_axi4_if.sv', 'amd_axi4_uvc_dpi_pkg.sv', 'uvmkit_pkg.sv', 'uvmkit_reg_pkg.sv', 'uvm_pkg.sv', 'cpaxi.v', 'cpaxi_common_defines_pkg.sv', 'cpaxi_core.v', 'cpaxi_reset.v',    'ati_rtr_staller.v', 'ifrit_delay.v', 'sr_bfm.sv', 'spi_sv_crawler_bfm.sv', 'gc_internal_monitors.v', 'tbtrk_cs_save.sv', 'spi_pc_baton_onehot_checker.sv', 'gc_utcl2_fcov.sv', 'gc_utcl2_vmapt_fcov.sv', 'sqc_staller.v', 'tb_clk_tbi.v', 'gc_ea_cli_fcov.sv', 'gc_ea_sdp_fcov.sv', 'gc_ea_misc_fcov.sv', 'hydra.sv', 'cp_utcl1_common_defines_pkg.sv', 'tb_clk_tbidyn.v', 'tb_assert_disa_tbi.v', 'tb_assert_disa_tbidyn.v', 'gc_rsmu_sideband_tbi.v', 'gc_rsmu_sideband_tbidyn.v', 'tb_ctrl_tbi.v', 'tb_ctrl_tbidyn.v', 'gc_cross_trigger_tbi.v', 'gc_cross_trigger_tbidyn.v', 'gc_sdp_port_control_monitor_tbi.v', 'gc_sdp_port_control_monitor_tbidyn.v', 'ngtb_reset_tbi.v', 'ngtb_reset_tbidyn.v']
        self.maint_file_list = ['cp.v', 'gc.v'] #, 'cpc.v', 'cp.v', 
        self.rtl_map = {
                '_monitor' : '../../ptb/env/debug/monitors'
                ,'_trace' : '../../ptb/env/debug/trace'
                ,'_shell' : '../shell'
                ,'gc_' : 'gc'
                ,'cp_' : 'cp'
                ,'cpc_' : 'cp/cpc'
                ,'cpf_' : 'cp/cpf'
                ,'cpg_' : 'cp/cpg'
                ,'cci' : 'cp/cci'
                ,'cpaxi' : 'cp/cpaxi'
                ,'gds' : 'gds'
                ,'ds_gds' : 'gds'
                ,'grbm' : 'grbm'
                ,'rlc_' : 'rlc'
                ,'tpi_' : 'tpi'
                ,'spi' : 'spi'
                ,'sx' : 'sx'
                ,'ds_' : 'lds'
                ,'lds_' : 'lds'
                ,'sqc' : 'sqc'
                ,'sq' : 'sq'
                ,'sp' : 'sp'
                ,'ta' : 'ta'
                ,'tc' : 'tc'
                ,'td' : 'td'
                ,'tcp' : 'tcp'
                ,'tcr' : 'tcr'
                ,'tcc' : 'tcc'
                ,'tca' : 'tca'
                ,'dbg' : '../misc/dbg' #unclassify
                ,'mut_adjust' : '../misc/define' #unclassify
                ,'ati' : 'shared/ati'
                ,'bpm' : 'shared/bpm'
                ,'gfx' : 'shared/gfx'
                ,'perfmon' : 'shared/perfmon'
                ,'px' : 'shared/px'
                ,'hy' : 'shared/hy'
                ,'ea_' : '../library/ea'
                ,'dft_' : '../library/dft'
                ,'utcl2_' : '../library/utcl2'
                ,'atcl2_' : '../library/atcl2'
                ,'rsmu_' : '../library/rsmu'
                ,'addr' : '../library/address'
                ,'dftmisc' : '../library/dftmisc'
                ,'rtllib' : '../library/rtllib'
                ,'vml2' : '../library/vml2'
                ,'axi' : '../library/axi_uvc-axi4'
                ,'atc_' : 'atc'
                ,'tci' : 'tci'
                ,'f32' : 'f32'
                #,'' : ''
                }
        self.incdir_map = {
                'vega20c/config/gc/pub/sim/fake_v_incl' : '/design/rtl/include/fake_v'
                ,'vega20c/config/gc/pub/sim' : ''
                ,'vega20c/library/rtllib-f18' : '/design/library/rtllib'
                ,'vega20c/library/dftmisc-vega20c' : '/design/library/dftmisc'
                ,'vega20c/library/gc-vega20c/pub/src/meta' : ''
                ,'vega20c/library/gc-vega20c/pub/src/verif' : ''
                ,'vega20c/library/gc-vega20c/pub/src/' : ''
                ,'vega20c/library/gc-vega20c' : '/design/library/gc'
                ,'vega20c/library/atcl2-hawaii' : '/design/library/atcl2'
                ,'vega20c/library/utcl2-hawaii' : '/design/library/utcl2'
                ,'vega20c/library/gmhubslib-hawaii' : '/design/library/gmhubslib'
                ,'vega20c/library/rsmu-bowenc_xcd_b0-gc/pub/src/meta' : ''
                ,'vega20c/library/rsmu-bowenc_xcd_b0-gc/' : '/design/library/rsmu'
                ,'vega20c/library/axi_uvc-axi4/pub/src/verif/amd_axi_uvc' : ''
                ,'vega20c/library/axi_uvc-axi4/pub/src/amd_sv' : ''
                ,'vega20c/library/axi_uvc-axi4' : '/design/library/axi_uvc-axi4'
                ,'vega20c/library/ea-hawaii' : '/design/library/ea'
                ,'vega20c/library/chiputils-gc' : ''
                ,'vega20c/library/address-vega20c-gfx8' : '/design/library/address'
                ,'vega20c/library/umclib-umc6_2a' : '/design/library/umclib-umc6_2a'
                ,'vega20c/library/vml2-hawaii' : '/design/library/vml2'
                ,'vega20c/library/vmlib-hawaii' : '/design/library/vmlib'
                ,'cmn/pub/src/verif/hydra' : ''
                ,'cmn/pub/src/verif/models' : ''
                ,'cmn/pub/src/rtl' : {
                    'header' : '/design/rtl/include/logic/'
                #,   'shell' : '/design/rtl/shell/'
                    }
                ,'cmn/pub/include/features' : '/design/misc/features'
                ,'cmn/pub/include/reg' : '/design/misc/reg'
                ,'cmn/pub/include/connectivity' : '/design/misc/connetivity'
                ,'cmn/pub/include/interfaces' : '/design/misc/interfaces'
                ,'cmn/pub/include/envs' : '/design/misc/envs'
                ,'cmn/pub/include' : {
                    'v_vh' : '/design/rtl/include/comm'
                    }
                ,'cmn/tmp' : '/design/misc/tmp'
                ,'verif/cp/tb/tb_cpgs/cmn' : ''
                ,'verif/td/tools/inc' : ''
                }
        self.cmt_instance = {
            'cp.v' : ['bpm_cpc', 'bpm_cpg', 'bpm_cpf_rep', 'cpaxi', 'cp_rep_Cpl_GFXCLK', 'bpm_cci', 'cci'],
            'cpc.v' : ['perfmon_state_sync', 'u_cpc_dbg_mux0', 'u_cpc_dbg_mux1', 'uccim', 'uccis', 'ucpc_ati_grbm_priv_intf', 'ucpc_cciu', 'ucpc_cg_sync_cpc_cpg', 'ucpc_cgtt_local_1r2d', 'ucpc_mec', 'ucpc_perfmon', 'ucpc_query_unit', 'ucpc_rbiu', 'ucpc_rciu', 'ucpc_reset', 'ucpc_roq_mec1', 'ucpc_roq_mec2', 'ucpc_save', 'ucpc_tciu', 'ucpc_utcl2_decode', 'ucpc_utcl2iu', 'ugfx_ecc_irritator_wrapper_0', 'ugfx_ecc_irritator_wrapper_1', 'ugfx_ecc_irritator_wrapper_2', 'vcpc_vbind'],
            'gc.v' : ['ea']
            }
        self.rtl2shell_def_list = ['rlc', 'cpc', 'cpg', 'cpf', 'bpmh', 'gc', 'cp', 'abv']
        self.cmt_module = {
            'cp.v' : ['bpm ', 'cpaxi ', 'cp_rep_Cpl_GFXCLK ', 'cci '],
            'cpc.v' : ['techind_syc_icd ', 'gfx_dbg_mux ', 'ccim ', 'ccis ', 'ati_grbm_priv_intf ', 'cpc_cciu ', 'cp_cg_sync ', 'gfx_cgtt_local_1r2d_wrapper ', 'cpc_mec ', 'cpc_perfmon ', 'cpc_query_unit ', 'cpc_rbiu ', 'cpc_rciu ', 'cpc_reset ', 'cpc_roq ', 'cpc_save ', 'cpc_tciu ', 'cp_utcl2_decode ', 'cpc_utcl2iu ', 'gfx_ecc_irritator_wrapper ', 'vcpc_module '],
            'gc.v' : ['gc_ea ']
            }
        self.cp_single_replace = '''        .cg_gfx_sclk(Cpl_GFXCLK)
        ,.cgcg_en(1'b1)
        ,.TTOP_P1_CPC_hard_resetb(RSMU_GFX_hard_resetb)
        ,.TTOP_P1_CPC_combined_resetb(RSMU_GFX_hard_resetb)
        ,.TTOP_P1_CPC_mem_power_ctrl(TTOP_CPC_P1_mem_power_ctrl)
        ,.TTOP_CPC_mgcg_override(0)
        ,.TTOP_CPC_fgcg_override(0)
        ,.TTOP_CPC_mgls_current_freq_code(0)
        ,.TTOP_CPC_mgls_override(0)\n'''
        self.vec_specified_files = ['tcc_tcr_rdata_monitor.v', 'tcrw_tcclient_ret_monitor.v', 'tcc_tcr_wdata_monitor.v', 'lds_sp_read_monitor.v', 'sp_lds_idx_monitor.v', 'tcclient_tcrw_hole_monitor.v', 'tcrw_tcclient_wr_ret_monitor.v']
        self.copy, self.error, self.skip = 17, 0, 0 # 17 means lib_so files, need add to total copy num
        self.incdir_files, self.all_files, self.relative_include = [], {}, {}
        self.reduced_files_set = set()
        self.all_files_set_g, self.all_files_set_filename = set(), set()
        self.all_files_set_v, self.all_files_set_v_filename, self.only_include_files = set(), set(), set()
        self.all_files_list_sum, self.all_files_list_sum_ = [], []
        self.abandon_file_suffix = ['log', 'dj', 'pub_spec', 'xml', 'txt', 'm4', 'ini', 'mk', 'mgr', 'xdl', 'mp', 'rb', 'tcl'] #, 'ale', 'bia', 'biah'
        self.ngtb_base_dir_list = [
                'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/../../../../../../../src/meta/tools/sp3/bin/',
                'out/../../../maintain_files/',
                'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/',
                'out/linux_3.10.0_64.VCS/vega20c/common/tmp/toolkit/hyvmt/verif_release_ro/basepkg_pkg/1.0.0/src/base/random/pli/VCS-D-2023.03-SP2-2/',
                'out/linux_3.10.0_64.VCS/common/pub/bin/',
                'out/linux_3.10.0_64.VCS/common/tmp/toolkit/hyvmt/verif_release_ro/tbhydra_pkg/1.0.7/src/base/mem/memio/c/lib/',
                'out/linux_3.10.0_64.VCS/vega20c/common/tmp/toolkit/hyvmt/verif_release_ro/tbhydra_pkg/1.0.7/src/base/mem/memio/pli/VCS-D-2023.03-SP2-2/',
                'out/linux_3.10.0_64.VCS/common/tmp/toolkit/hyvmt/verif_release_ro/basepkg_pkg/1.0.0/src/message/msgio/c/',
                'out/linux_3.10.0_64.VCS/vega20c/common/tmp/toolkit/hyvmt/verif_release_ro/basepkg_pkg/1.0.0/src/message/msgio/pli/VCS-D-2023.03-SP2-2/',
                'out/linux_3.10.0_64.VCS/common/tmp/toolkit/hyvmt/verif_release_ro/connectivity_pkg/1.0.6/interface/src/vecio/c/',
                'out/linux_3.10.0_64.VCS/vega20c/common/tmp/toolkit/hyvmt/verif_release_ro/connectivity_pkg/1.0.6/interface/src/vecio/pli/VCS-D-2023.03-SP2-2/',
                'out/linux_3.10.0_64.VCS/common/tmp/toolkit/hyvmt/verif_release_ro/basepkg_pkg/1.0.0/src/datatypes/quadstate/',
                'out/linux_3.10.0_64.VCS/vega20c/common/tmp/src/verif/sh/tools/cmn/',
                'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/',
                'out/linux_3.10.0_64.VCS/vega20c/library/gc-vega20c/tmp/src/meta/tools/sp3/lib/',
                'out/linux_3.10.0_64.VCS/vega20c/common/tmp/src/verif/sh/tools/sh_meta/',
                ]
        self.pvtb_tab_file_list = [
            'ati_random.tab',
            'libati_random_pli.so',
            'libmemio.so',
            'libmemio_pli.so',
            'libmsgio.so',
            'libmsgio_pli.so',
            'libvecio.so',
            'libvecio_pli.so',
            'memio.tab',
            'msgio.tab',
            'vecio.tab',
            'libquadstate.so',
            'libsh_bfm_common_dpi.so',
            'libsp3.so.1',
            'libsp3_disasmble.so',
            'libsh_meta.so',
            'libdummy_sc_main.so'
            ]


    def flist_for_copy(self, flist, cp_out_flist, old_few_incdir, more):
        with open(flist, 'r') as f:
            lines = f.readlines()
        ## For copy file
        #rtl_lines = [line.split('//')[0].lstrip('-v').strip() for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('+') and not line.strip().startswith('-v ') and 'arch' in line]
        cleaned_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('+')]
        ## Public incdir lines 
        pub_incdir_lines = []
        for line in lines:
            if line.strip().startswith('+') and 'arch' not in line:# and not line.strip().startswith('//') :
                pub_incdir_lines.append(line)
        #if more:
        with open(cp_out_flist, 'w') as f:
            f.write('\n'.join(cleaned_lines))
        with open(old_few_incdir, 'w') as incf:
            incf.write(''.join(pub_incdir_lines))
        return cleaned_lines

    def get_now(self, which='dhms', delimiter=False):
          #[tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst]
        now= list(time.localtime())
        now= [str(i).zfill(2) for i in now] 
        def case(var):
            return {
                ('all', True): str(now[0]+'/'+now[1]+'/'+now[2]+' '+now[3]+':'+now[4]+':'+now[5]),
                ('dhms', True): str(now[2]+' '+now[3]+'-'+now[4]+'-'+now[5]),
                ('ymd', True): str(now[0]+'-'+now[1]+'-'+now[2]),
                ('all', False): str(now[0]+now[1]+now[2]+now[3]+now[4]+now[5]),
                ('dhms', False): str(now[2]+now[3]+now[4]+now[5])
            }.get(var, "[get_now]Wrong request")
        return case((which, delimiter))

    def change_path2stem(self, src_flist, target, more):
        tree_name = target.split('/')[-2]
        ptn = re.compile('/project[\w/-]+' + tree_name)
        with open(src_flist, 'r') as infile, \
             open(src_flist + '_2stem', 'w') as outfile1:
            for line in infile:
                modified_line = ptn.sub('$STEM', line)
                outfile1.write(modified_line)

    def gen_rtl_f(self, target, rtl_src, inc_src, old_few_incdir):
        relative_lines = []
        with open(rtl_src, 'r') as f1:
            lines_rtl = [line.rstrip('\n') for line in f1]
        with open(inc_src, 'r') as f2:
            set_rtl = set(lines_rtl)
            incdir_set, incdir_list = set(), []
            unique_lines_inc = [] # if include files not in rtl, make it become -v
            for line in f2:
                cleaned_line = line.rstrip('\n')
                dir_path = os.path.dirname(cleaned_line)
                dir_path_dir = os.path.normpath(dir_path)
                if not dir_path:
                    dir_path = '.'
                elif dir_path_dir not in incdir_set: # get new +incdir+
                    incdir_list.append(f"+incdir+{dir_path_dir}\n")
                    incdir_set.add(dir_path_dir)
                if cleaned_line not in set_rtl:
                    unique_lines_inc.append(f"-v {cleaned_line}\n")
        with open(old_few_incdir) as f3: # old 5 +incdir+ 
            lines_old_inc = f3.readlines()
        relative_lines.extend([f'-v {target}src/design/misc/{key}\n' for key, value in self.relative_include.items()]) # 8 relative include files
        merged_content = incdir_list + lines_old_inc + [f"{line}\n" for line in lines_rtl]
        #merged_content = incdir_list + lines_old_inc + unique_lines_inc + relative_lines + [f"{line}\n" for line in lines_rtl]
        os.makedirs(target + self.project + '/ptb', exist_ok = True)
        ### dir to $STEM
        tree_name = target.split('/')[-2]
        ptn = re.compile('/project[\w/-]+' + tree_name)
        with open(target + self.project + '/ptb/rtl.f', 'w') as outfile:
            for file in merged_content:
                #outfile.write(file)
                modified_line = ptn.sub('$STEM', file)
                outfile.write(modified_line)

    def gen_rtl_f_1(self, target, inc_src, rtl_src):
        with open(inc_src, 'r') as f1:
            lines_inc = [line.rstrip('\n') for line in f1]
        with open(src_rtl, 'r') as f2:
            set_inc = set(lines_inc)
            unique_lines_inc = []
            for line in f2:
                cleaned_line = line.rstrip('\n')
                if cleaned_line not in set_rtl:
                    unique_lines_inc.append(f"-v {cleaned_line}\n")
        merged_content = unique_lines_inc + [f"{line}\n" for line in lines_inc]
        os.makedirs(target + self.project + '/ptb', exist_ok = True)
        with open(target + self.project + '/ptb/rtl.f', 'w') as outfile:
            for file in merged_content:
                outfile.write(file)
    
    def copy2file(self, target, src_file, target_file):
        tar_path, tar_file = os.path.split(target_file)
        os.makedirs(tar_path, exist_ok = True)
        try:
            self.rm_one_file(target_file)
            shutil.copy2(src_file, tar_path)
            self.copy += 1
            #print(src_file)
        except Exception as e:
            #print("Error: copy failed: %s -> %s" % (src_file, e))
            copy_log = '\nError: copy failed: -> ' + str(e)
            with open(target + '/logs/ngtb2ptb.log', 'a+') as f:
                f.write(copy_log)
            self.skip += 1

    def copy_a_path(self, target, src_dir, tar_dir, sub_dir):
        for root, dirs, files in os.walk(src_dir):
            #rel_path = os.path.relpath(root, src_dir)
            #dest_dir_path = os.path.join(tar_dir, rel_path)
            os.makedirs(tar_dir, exist_ok = True)
            for file in files:
                file_suffix = file.split('.')[-1]
                if file_suffix in self.abandon_file_suffix:
                    continue
                src_file = os.path.join(root, file)
                new_line = self.get_rtl_filter_2copy(target, src_file, rtl_flag = False)
                #dst_file = os.path.join(tar_dir, file)
                #if src_file not in self.incdir_files:
                #    self.incdir_files.append(src_file + '\n')
                #    if 'common/pub/src/rtl' in src_dir:
                #        if '_shell' in file:  
                #            self.copy2file(target, src_file, target + self.project + sub_dir['shell']) 
                #        else:
                #            self.copy2file(target, src_file, target + self.project + sub_dir['header']) 
                #    else:
                #        self.copy2file(target, src_file, dst_file)
                #else:
                #    pass

    def get_incdir_filter_2copy(self, target, line, reduced_flist, incdir_all_flist):
        multi_line, reduce_incdir = [], []
        for k, v in self.incdir_map.items():
            if k in line and isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    new_line = os.path.normpath(target + self.project) + sub_v 
                    multi_line.append('+incdir+' + new_line + '\n')
                    self.copy_a_path(target, line.split('+')[2], new_line, sub_v)
                map_line = ''.join(multi_line)
                break
            elif k in line and isinstance(v, str) and v != '':
                new_line = target + self.project + v
                map_line = '+incdir+' + new_line + '\n'
                self.copy_a_path(target, line.split('+')[2], new_line, v)
                break
            else:
                ###map_line = line + '\n'  #for_debug, don't copy 'vega20c/config/gc/pub/sim'
                map_line = ''
            if k in line and v == '':
                if line in str(reduce_incdir):
                    pass
                else:
                    reduce_incdir.append(line + '\n')
        with open(reduced_flist, 'a+') as rf:
            rf.write(''.join(reduce_incdir)) 
        #with open(incdir_all_flist, 'w') as incf:
        #    incf.write(''.join(self.incdir_files))
        return map_line

    def get_rtl_filter_2copy(self, target, line, rtl_flag):
        filename = os.path.basename(line) #.split('.')[0]
        if filename not in self.all_files or rtl_flag == True:
            #if 'cpg_shell' in line: #std_ovl_clock, std_ovl_clock, std_ovl_init, have not copy 3 common files
            #    print('1')
            if filename in self.all_files:
                already_copy = True
            else:
                already_copy = False
            if os.path.islink(line):
                map_line = os.path.realpath(line)
            else:
                map_line = line
            for k, v in self.rtl_map.items():
                filename_ = filename.split('.')[0]
                if filename_.startswith(k) or filename_.endswith(k):
                    classify = v
                    break
                else:
                    classify = 'misc' #unclassify
                    pass
            if 'cp.v' == os.path.basename(line):
                new_line = os.path.join(target + self.project + '/design/shell/cp_with_cpg_cpf_cpc.v')
            elif 'gc.v' == os.path.basename(line):
                new_line = os.path.join(target + self.project + '/design/shell/gc_without_ea.v')
            elif classify == 'misc':
                new_line = os.path.join(target + self.project + '/design/' + classify + '/', os.path.basename(line))
            else:
                new_line = os.path.join(target + self.project + '/design/rtl/' + classify + '/', os.path.basename(line))
            if 'arch' not in line:
                pass # common files e.g. /proj/tools/....
            else:
                self.all_files[filename] = line
                if not already_copy:
                    self.copy2file(target, line, new_line)
                    pass
        else:
            new_line = self.all_files[filename]
        return new_line

    def mpp_path_flist(self, source_flist, target_flist, target, reduced_flist, incdir_all_flist, more):
        tar_lines = []
        with open(source_flist, 'r') as sf:
            lines = sf.readlines()
        comp_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//')]
        for line in comp_lines:
            parts = line.split()
            if 'arch' not in line:
                tar_lines.append(line + '\n')
                continue
            elif '+incdir+' in line:
                map_line = self.get_incdir_filter_2copy(target, line, reduced_flist, incdir_all_flist)
                if map_line in tar_lines:
                    continue
                tar_lines.append(map_line)
                continue
            elif len(parts) < 2:
                rtl_flag = True
                new_line = self.get_rtl_filter_2copy(target, line, rtl_flag)
                tar_lines.append(new_line + '\n')
                continue
            elif len(parts) == 2: # with -v, add -v after line used
                rtl_flag = True
                new_line = self.get_rtl_filter_2copy(target, parts[1], rtl_flag)
                new_file_path = os.path.join(parts[0] + ' ', new_line)
                tar_lines.append('-v ' + new_file_path + '\n')
                continue
        with open(target_flist, 'w') as f:
            f.write(''.join(tar_lines))
       
    def flist_delete_cmt(self, target, flist, ngtb_all_cmt_flist, rtl_target, more):
        with open(flist, 'r') as f:
            lines = f.readlines()
        with open(ngtb_all_cmt_flist, 'w') as f:
            comp_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//')]
            f.write('\n'.join(comp_lines))

    def copy_rtl_files(self, flist, target_dir, preserve_structure=True, more=True):
        success, skips, errors = 0, 0, 0
        os.makedirs(target_dir, exist_ok = True)
        #flist_cp = self.flist_for_copy(flist, cp_out_flist, more)
        ###with open(cp_out_flist, 'r') as f:
        ###    files = [line.strip() for line in f.readlines() if line.strip()]
        for src_path in flist_cp:
            if not os.path.exists(src_path):
                #print("Error: file not exist: {}".format(src_path))
                errors += 1
                continue
            if preserve_structure:
                ## Preserve the original path structure
                ## e.g. (/src/path/file.txt -> /target_dir/src/path/file.txt)
                relative_path = os.path.relpath(src_path, start=os.path.dirname(target_dir))
            else:
                relative_path = os.path.basename(src_path)
            dest_path = os.path.join(target_dir, relative_path)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok = True)
            if 'arch' not in src_path:
                continue
            try:
                self.rm_one_file(dest_path)
                shutil.copy2(src_path, dest_path)
                success +=1
            except Exception as e:
                #print("Error: copy failed: %s -> %s" % (src_path, e))
                skips += 1
        print("    - rtl succeeded files: {}".format(success))
        print("    - rtl skipped files: %s" % skips)
        print("    - rtl errors files: %s" % errors)
    
    def get_incdir_dir(self, line, out_target):
        vega_idx = 0
        src_dir = line.split('+incdir+')[1]
        if not any(item in line for item in ['verif/td', 'verif/cp']):
            vega_idx = line.split('/').index('out') + 2  ## get vega20c's index
        if line.split('/')[vega_idx] == 'vega20c':
            tar_dir = out_target + '/'.join(src_dir.split('/')[vega_idx :])
        elif line.split('/')[vega_idx] == 'common':
            tar_dir = out_target + 'vega20c/' + '/'.join(src_dir.split('/')[vega_idx :])    
        elif any(item in line for item in ['verif/td', 'verif/cp']):
            tar_dir = out_target + 'vega20c/library/gc-vega20c/pub/src/verif/'
        return tar_dir, src_dir
    
    def copy_incdir_file(self, flist, target, more):
        s_sum, c_sum, e_sum = 0, 0, 0
        out_target = target + 'src/' if target.endswith('/') else target + '/src/'
        with open(flist, 'r') as f:
            lines = f.readlines()
        incdir_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//') and '+incdir+' in line]
        for line in incdir_lines:
            if 'arch' in line:
                tar_dir, src_dir = self.get_incdir_dir(line, out_target)
                skipped, copied, errors = self.copy_one_path(src_dir, tar_dir, more)
            s_sum += skipped
            c_sum += copied
            e_sum += errors
        print("    - out copied files: {}".format(c_sum))
        print("    - out skipped files: {}".format(s_sum))
        if more: print("    - out copied error files: %s" % e_sum)
    
    def create_folder(self, target):
        folder_list = [
                        '/ptb',
                        '/psm',
                        '/gkt',
                        '/../out/compile/cache_sanity_test',
                        '/../out/run/cache_sanity_test'
                        ]
        for dir in folder_list:
            os.makedirs(target + self.project + dir, exist_ok = True)
    
    def copy_one_path(self, src_dir, tar_dir, more):
        copied, skipped, errors = 0, 0, 0
        for root, dirs, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            dest_dir_path = os.path.join(tar_dir, rel_path)
            os.makedirs(dest_dir_path, exist_ok = True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir_path, file)
                try:
                    self.rm_one_file(dst_file)
                    shutil.copy2(src_file, dst_file)
                    copied+=1
                except Exception as e:
                    #if more: print("Copy fail: {} --> {}".format(src_file, e))
                    errors += 1
        return skipped, copied, errors
    
    def tab_flist_only_copy(self, ngtb_base_dir, target, appended_flist, more):
        s_sum, c_sum, e_sum = 0, 0, 0
        tab_flist = []
        tab_target = target + self.project + '/ptb/env/debug/lib_so'
        for dir in self.ngtb_base_dir_list:
            src_dir = ngtb_base_dir + dir 
            for root, dirs, files in os.walk(src_dir):
                rel_path = os.path.relpath(root, src_dir)
                dest_dir_path = os.path.join(tab_target, rel_path)
                for file in self.pvtb_tab_file_list:
                    if file in files:
                        os.makedirs(dest_dir_path, exist_ok = True)
                        try:
                            self.rm_one_file(tab_target + file)
                            if file == 'libsp3.so.1':
                                shutil.copy2(src_dir + '/' + file, tab_target + '/' + 'libsp3.so')
                            else:
                                shutil.copy2(src_dir + '/' + file, tab_target)
                            if file in str(tab_flist):
                                pass
                            else:
                                tab_flist.append('\n' + src_dir + '/' + file)
                        except:
                            pass
        self.rm_tree_dir(target + self.project + '/ptb/env/debug/lib_so/sim')
        with open(appended_flist,'a+') as f:
            f.write(''.join(tab_flist))
        if more:
            for dir in self.ngtb_base_dir_list:
                ngtb_base_dir_ = ngtb_base_dir + dir 
                skipped, copied, errors = self.copy_one_path(ngtb_base_dir_, tab_target, more)
                s_sum += skipped
                c_sum += copied
                e_sum += errors
            print("    - tab copied files: {}".format(c_sum))
            print("    - tab skipped files: {}".format(s_sum))
            print("    - tab copied error files: %s" % e_sum)
    
    def relative_include_copy(self, target):
        for key, src_line in self.relative_include.items():
            r_dir, file_name = key.split('/')
            tar_line = target + 'src/design/misc/' + r_dir
            os.makedirs(tar_line, exist_ok = True)
            filename = os.path.basename(src_line) #.split('.')[0]
            #if 'sqc_features' in src_line:
            #    print('1')
            if filename in self.all_files:
                already_copy = True
            else:
                already_copy = False
            if already_copy:
                self.copy -= 1 # if already copy, copy again, and subtract 1
                self.copy2file(target, src_line, tar_line + '/' + file_name)
            elif not already_copy:
                self.copy2file(target, src_line, tar_line + '/' + file_name)
            if filename not in self.all_files:
                if 'sqc_features' in src_line:
                    self.copy -= 1 # if is sqc_features.svh, this copy twich, because relative path, so, this copy number need subtract 1
                    continue
                self.all_files[filename] = src_line

    def ngtb_v_inc_only_copy(self, target, src_flist,  ngtb_base_dir):
        include_ngtb_v_flist_copy = target + "logs/v_include_ngtb_flist_copy.xf"
        only_include_file = target + "logs/only_include_flist.xf"
        include_tmp_flist_in = target + "logs/incdir_tmp_flist_in.xf"
        include_tmp_flist_out = target + "logs/incdir_tmp_flist_out.xf"   
        inc_dirs, files, queue = [], [], []
        all_files_set, unfind_files_set, tmp_set = set(), set(), set()
        with open(src_flist, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('+incdir+'):
                    parts = line[8:].split()
                    inc_dirs.extend(parts)
                elif line.startswith('-v '):
                    if 'arch' not in line:
                        files.append(line.split(' ')[-1]) # get public files's include 
                        continue
                    elif line:  # only get -v files 
                        files.append(line.split(' ')[-1])
        files.append(target + 'src/design/shell/cpc_shell.v')
        for file in files:
            abs_path = os.path.abspath(file.strip())
            if abs_path not in all_files_set:
                queue.append(abs_path)
                all_files_set.add(abs_path)
            filename = abs_path.split('/')[-1]
            if filename not in self.all_files_set_v_filename:
                self.all_files_set_v.add(abs_path)
                self.all_files_set_v_filename.add(filename)
        while queue:
            current_file = queue.pop(0)
            current_dir = os.path.dirname(current_file)
            includes = self.extract_includes(current_file) # only find -v include files
            for inc in includes:
                inc_file_path = self.find_include_file(inc, current_dir, inc_dirs, ngtb_base_dir)
                if inc_file_path:
                    if '/' in inc: # get relative include files and copy it to misc
                        if inc not in self.relative_include:
                            self.relative_include[inc] = inc_file_path
                            if inc_file_path in all_files_set: # if file in relative include, need delete repeated files
                                all_files_set.discard(inc_file_path)
                    if inc_file_path not in all_files_set and '/' not in inc: #append new include file
                        all_files_set.add(inc_file_path)
                        tmp_set.add(inc_file_path)
                        queue.append(inc_file_path)   
                    if inc_file_path not in self.only_include_files:
                        self.only_include_files.add(inc_file_path)
                elif inc_file_path == None: # can not find include file
                    if inc not in unfind_files_set:
                        unfind_files_set.add(inc)
        #with open(out_flist, 'w') as out_f:
        #    for file_path in all_files_set:
        #        out_f.write(file_path + '\n')
        with open(include_ngtb_v_flist_copy, 'w') as out_f:
            for file_path in self.all_files_set_v:
                out_f.write(file_path + '\n')
        with open(include_tmp_flist_in, 'w') as out_f:
            for file_path in tmp_set: 
                out_f.write(file_path + '\n')
                if file_path not in self.all_files_set_v: # copy new include file
                    new_line = self.get_rtl_filter_2copy(target, file_path, rtl_flag = True)
        with open(include_tmp_flist_out, 'w') as out_f:
            for file_path in all_files_set:
                out_f.write(file_path + '\n')
        if self.j != 0:
            self.j -= 1
            self.ngtb_v_inc_only_copy(target, include_tmp_flist_in, ngtb_base_dir)
        #with open(target + 'logs/unfind_files.xf', 'a+') as uf:
        #    for file_name in unfind_files_set:
        #        uf.write(file_name + '\n')
        with open(only_include_file, 'w') as onf:
            for file_path in self.only_include_files:
                onf.write(file_path + '\n')

    def flist_change_shell(self, ngtb_base_dir, target, filename, last_flist, reduced_flist, appended_flist, more):
        with open(filename, 'r') as file:
            lines = file.readlines()
        modified_lines, reduced_lines, appended_lines = [], [], []
        for line in lines:
            modifier = False
            shell_file_name = line.strip().split('/')[-1]
            for shell_file in self.shell_list:
                shell_related_ptn = r'^' + shell_file + '.*\.'
                if shell_file + '.v' == shell_file_name or shell_file + '.sv' == shell_file_name:
                    modifier = True
                    #new_line = line.replace(shell_file + '.v', shell_file + '_shell.v')
                    #if shell_file == 'cp':
                    #    new_shell_name = 'cp_with_cpg_cpf_cpc.v\n'
                    #elif shell_file == 'cpc':
                    #    new_shell_name = 'cpc_only_dc0.v\n'
                    #elif shell_file == 'gc':
                    #    new_shell_name = 'gc_without_ea.v\n'
                    #else:
                    new_shell_name = shell_file + '_shell.v\n'
                    #new_line = '//pvtb_shell//' + line + target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/' + new_shell_name
                    new_line = ngtb_base_dir + 'out/linux_3.10.0_64.VCS/vega20c/common/pub/src/rtl/bia_ifrit_logical/' + new_shell_name
                    if line not in self.reduced_files_set:
                        self.reduced_files_set.add(line)
                    appended_lines.append(new_line)
                    modified_lines.append(new_line)
                elif re.search(shell_related_ptn, shell_file_name) and shell_file + '_shell.v' != shell_file_name:
                    #if any(item in line for item in ['cpc_dc', 'cpc_mem', 'cpc_rfp', 'gds_mem']):
                    #    modifier = True
                    #    modified_lines.append(line)
                    #    reduced_lines.append(line)
                    #else:
                    #    modifier = True
                    #    modified_lines.append('//pvtb_shell// {}'.format(line))
                    #    reduced_lines.append(line)
                    if any(item in line for item in self.cmt_sv_list):
                        if shell_file == 'cp':
                            break
                        modifier = True
                        #modified_lines.append('//pvtb_shell// {}'.format(line))
                        if line not in self.reduced_files_set:
                            self.reduced_files_set.add(line)
                            #reduced_lines.append(line)
                    elif not modifier:
                        modifier = True
                        modified_lines.append(line)
                        #reduced_lines.append(line)
                elif not modifier:
                    modifier = True
                    have_flag = 0
                    for shell_file in self.shell_list:
                        if shell_file + '.v' == shell_file_name or shell_file + '.sv' == shell_file_name or any(item in line for item in self.cmt_sv_list):
                            have_flag = 1
                            break
                    ### After first string 'cpf', will append twice, this code ensure only generate once
                    #for shell_file in self.shell_list:
                    #    shell_related_ptn = r'^' + shell_file + '.*\.'
                    #    if re.search(shell_related_ptn, shell_file_name) and shell_file + '_shell.v' != shell_file_name:  
                    #        have_flag = 1
                    #        #modified_lines.append(line)
                    #        #reduced_lines.append(line)
                    #        break
                    if shell_file_name == 'tb_gc.sv':
                        continue
                    elif not have_flag:
                        modifier = True
                        modified_lines.append(line)
        #line_pvtb = target + 'pvtb/from_timescale.compfiles.bwc.xf\n'
        for vec_file in self.vec_specified_files:
            line_pvtb = '\n' + ngtb_base_dir + 'out/linux_3.10.0_64.VCS/vega20c/common/pub/include/interfaces/' + vec_file
            appended_lines.append(line_pvtb)
            modified_lines.append(line_pvtb)
        with open(appended_flist, 'w') as file:
            file.writelines(appended_lines)
        with open(last_flist, 'w') as file:
            file.writelines(modified_lines)
        with open(reduced_flist, 'w') as file:
            file.writelines(self.reduced_files_set)

    def appended_files_from_source_to_flist(self, ngtb_base_dir, ngtb_rtl_cmt_flist, last_rtl_flist):
        with open(ngtb_rtl_cmt_flist, 'r') as cf:
            orig_lines = cf.readlines()
        orig_lines[-1] = orig_lines[-1] + '\n'
        for spcf_file in self.vec_specified_files:
            orig_lines.append(ngtb_base_dir + 'out/linux_3.10.0_64.VCS/vega20c/common/pub/include/interfaces/' + spcf_file + '\n')
        with open(last_rtl_flist, 'w') as lf:
            lf.write(''.join(orig_lines))

    def parse_flist(self, filelist_path):
        inc_dirs = []
        files, files_ = [], []
        with open(filelist_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('+incdir+'):
                    parts = line[8:].split()
                    inc_dirs.extend(parts)
                elif line.startswith('-v '):
                    continue
                elif 'arch' not in line:
                    continue
                else:  # only get rtl files 
                    if line:
                        files.append(line.split(' ')[-1])
                        #files_.append(line) # for write a file with -v
        return inc_dirs, files

    def find_include_file(self, include_name, current_file_dir, inc_dirs, ngtb_base_dir):
        if os.path.isabs(include_name):
            if os.path.exists(include_name):
                return include_name
        else:
            possible_paths = []
            possible_paths.append(os.path.join(current_file_dir, include_name))
            for inc_dir in inc_dirs:
                possible_paths.append(os.path.join(inc_dir, include_name))
            for path in possible_paths:
                if os.path.exists(path):
                    return os.path.abspath(path)
            #for root, dirs, files in os.walk(ngtb_base_dir + '/out/linux_3.10.0_64.VCS/vega20c'):
            #    for file in files:
            #        if file == os.path.basename(include_name):
            #            file_path = os.path.join(root, file)
            #            if os.path.exists(file_path):
            #                return os.path.abspath(file_path)
        return None
    
    def extract_includes(self, file_path):
        include_pattern = re.compile(r'`include\s+"([^"]+)"')
        includes = []
        try:
            with open(file_path, 'r', errors = 'ignore') as f:
                content = f.read()
            includes = include_pattern.findall(content)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        return includes

    def get_include_file(self, target, src_flist, out_flist, ngtb_base_dir):
        only_include_file = target + "logs/only_include_flist.xf"
        include_all_flist = target + "logs/incdir_all_flist.xf"   # ngtb source file list
        include_all_flist_copy = target + "logs/incdir_all_flist_copy.xf"
        include_tmp_flist_in = target + "logs/incdir_tmp_flist_in.xf"
        include_tmp_flist_out = target + "logs/incdir_tmp_flist_out.xf"
        inc_dirs, files = self.parse_flist(src_flist)
        all_files_set, unfind_files_set = set(), set()
        all_files_list_1, all_files_list_2 = [], []
        tmp_set = set()
        queue= []
        #with open(src_flist, 'r') as sf:
        #    files = sf.readlines()
        for file in files:
            abs_path = os.path.abspath(file.strip())
            if abs_path not in all_files_set:
                queue.append(abs_path)
                all_files_set.add(abs_path)
                all_files_list_1.append(abs_path)
            filename = abs_path.split('/')[-1]
            if filename not in self.all_files_set_filename:
                self.all_files_set_g.add(abs_path)
                self.all_files_set_filename.add(filename)
        while queue:
            current_file = queue.pop(0)
            current_dir = os.path.dirname(current_file)
            includes = self.extract_includes(current_file) # only rtl, no -v, no public file
            for inc in includes:
                inc_file_path = self.find_include_file(inc, current_dir, inc_dirs, ngtb_base_dir)
                if inc_file_path: # get relative include files and copy it to misc
                    if '/' in inc:
                        if inc not in self.relative_include:
                            self.relative_include[inc] = inc_file_path
                            if inc_file_path in all_files_set: # if file in relative include, need delete repeated files
                                all_files_set.discard(inc_file_path)

                    if inc_file_path not in all_files_set and '/' not in inc: #append new include file
                        if 'gmhubslib' in inc_file_path and 'block_hierarchy' in inc_file_path: # don't use files under 'gmhubslib' path
                            continue
                        all_files_set.add(inc_file_path)
                        all_files_list_2.append(inc_file_path)
                        tmp_set.add(inc_file_path)
                        queue.append(inc_file_path)
                    if inc_file_path not in self.only_include_files:
                        self.only_include_files.add(inc_file_path)
                elif inc_file_path == None: # can not find include file
                    if inc not in unfind_files_set:
                        unfind_files_set.add(inc)
        all_files_list_1.reverse()
        all_files_list_2.reverse()
        self.all_files_list_sum += all_files_list_1
        self.all_files_list_sum += all_files_list_2 # get the include order: file 987, 654, 654, 321
        self.all_files_list_sum_ = self.all_files_list_sum
        self.all_files_list_sum_.reverse()
        #print(f'Unfind the file: {unfind_files_set}')
        #print(f'Total {len(unfind_files_set)} files can not find')
        with open(out_flist, 'w') as out_f:
            for file_path in self.all_files_list_sum_:
                out_f.write(file_path + '\n')
        with open(include_all_flist, 'w') as out_f:
            for file_path in self.all_files_list_sum_:
                out_f.write(file_path + '\n')
        with open(include_tmp_flist_in, 'w') as out_f:
            for file_path in tmp_set:
                out_f.write(file_path + '\n')
        with open(include_tmp_flist_out, 'w') as out_f:
            for file_path in all_files_set:
                out_f.write(file_path + '\n')
        if self.i != 0:
            self.i -= 1
            self.get_include_file(target, include_tmp_flist_in, include_tmp_flist_out, ngtb_base_dir)
        #with open(target + 'logs/unfind_files.xf', 'w') as uf:
        #    for file_name in unfind_files_set:
        #        uf.write(file_name + '\n')
        with open(only_include_file, 'w') as onf:
            for file_path in self.only_include_files:
                onf.write(file_path + '\n')

    def flist_cmt_sub_module(self, target, source_flist, reduced_flist): 
        with open(source_flist, 'r') as file:
            src_lines = file.readlines()
        with open(reduced_flist, 'r') as file:
            rdc_lines = file.readlines()
        modified_lines, reduced_lines = [], []
        for line in src_lines:
            modifier = False
            shell_file_name = line.strip().split('/')[-1]
            for spf_file in self.cmt_specific_list:
                if spf_file == shell_file_name:
                    #line = '//pvtb_shell// ' + line
                    if line not in self.reduced_files_set:
                        self.reduced_files_set.add(line)
                        #reduced_lines.append(line)
                    line = ''
                    break
            if line:
                for shell_file in self.shell_sub_module_list:
                    shell_related_ptn = r'^' + shell_file + '.*\.'
                    if re.search(shell_related_ptn, shell_file_name) and shell_file + '_shell.v' != shell_file_name:
                        if any(item in line for item in self.cmt_sv_list):
                            modifier = True
                            modified_lines.append(line)
                        elif any(item in line for item in self.shell_sub_module_list):
                            modifier = True
                            #modified_lines.append('//pvtb_shell// {}'.format(line))
                            if line in str(rdc_lines):
                                pass
                            else:
                                if line not in self.reduced_files_set:
                                    self.reduced_files_set.add(line)
                                #reduced_lines.append(line)
                        elif not modifier:
                            modifier = True
                            modified_lines.append(line)
                    elif not modifier:
                        modifier = True
                        have_flag = 0
                        for shell_file in self.shell_sub_module_list:
                            shell_related_ptn = r'^' + shell_file + '.*\.'
                            if any(item in line for item in self.shell_sub_module_list) and shell_file + '_shell.v' != shell_file_name and re.search(shell_related_ptn, shell_file_name):
                        #if re.search(shell_related_ptn, shell_file_name):
                                have_flag =1
                                break
                        ### After first string 'cpf', will append twice, this code ensure only generate once
                        if not have_flag:
                            modifier = True
                            modified_lines.append(line)
        with open(source_flist, 'w') as file:
            file.writelines(modified_lines)
        with open(reduced_flist, 'w') as file:
            file.writelines(self.reduced_files_set)

    def only_get_rtl_and_cmt_flist(self, target, src_flist, rtl_out_flist, cmt_v_flist):
        with open(src_flist, 'r') as f:
            lines = f.readlines()
        ## For only rtl file
        rtl_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('+') and not line.strip().startswith('-v ')]
        cmt_v_lines = [line.split('//')[0].strip() for line in lines if line.strip() and line.strip().startswith('-v ') and 'arch' not in line]
        ## Public incdir lines 
        pub_incdir_lines = []
        for line in lines:
            if line.strip().startswith('+') and 'arch' not in line:# and not line.strip().startswith('//') :
                pub_incdir_lines.append(line)
        #if more:
        with open(cp_out_flist, 'w') as f:
            f.write('\n'.join(cleaned_lines))
        with open(old_few_incdir, 'w') as incf:
            incf.write(''.join(pub_incdir_lines))
        with open(only_rtl_flist, 'w') as wf:
            wf.write(files)

    def maintain_file2shell(self, target, more):
        for file in self.maint_file_list:
            with open(target + self.project + '/design/shell/' + file, 'r') as f:
                file_cont = f.readlines()
            define_flag, cmt_lines = 0, []
            for line in file_cont:
                if any(item in line for item in self.cmt_module[file]) and any(item in line for item in self.cmt_instance[file]):
                    define_flag = 1
                    leading_spaces = line[:len(line) - len(line.lstrip())]
                    #if file == 'cp.v':
                    #    line = leading_spaces + '`ifndef PVTB_CP_SHELL\n' + line
                    #elif file == 'cpc.v':
                    #    line = leading_spaces + '`ifndef PVTB_CPC_SHELL\n' + line
                    if file == 'gc.v':
                        line = leading_spaces + '`ifndef PVTB_EA_RTL_OMIT\n' +line
                    cmt_lines.append(line)
                elif ');' in line.strip() and define_flag == 1:
                    if file == 'cp.v':
                        cmt_lines.append(line)
                        continue
                    define_flag = 0
                    leading_spaces = line[:len(line) - len(line.lstrip())]
                    line += leading_spaces + '`endif\n'
                    cmt_lines.append(line)
                elif all(item not in line for item in self.cmt_instance[file]):
                    cmt_lines.append(line)
                else:
                    cmt_lines.append(line)
            if file == 'cp.v':
                with open(target + self.project + '/design/shell/cp_with_cpg_cpf_cpc.v', 'w') as f:
                    f.write(''.join(cmt_lines))
            #elif file == 'cpc.v':
            #    with open(target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cpc_only_dc0.v', 'w') as f:
            #        f.write(''.join(cmt_lines))
            elif file == 'gc.v':
                with open(target + self.project + '/design/shell/gc_without_ea.v', 'w') as f: 
                    f.write(''.join(cmt_lines))

    def file_replace_lines(self, target, more):
        file_name = target + self.project + '/design/shell/cp_with_cpg_cpf_cpc.v'
        with open(file_name, 'r') as file:
            lines = file.readlines()
        new_lines, i = [], 0
        while i < len(lines):
            line = lines[i]
            if 'cpc cpc' in line:
                i += 1
                new_lines.append(line)
                i += 9
                new_lines.extend(self.cp_single_replace)
            else:
                new_lines.append(line)
                i += 1
        with open(file_name, 'w') as f:
            f.writelines(new_lines)

    def file_cmt_lines(self, target, more):
        file_name = target + self.project + '/design/shell/cpg_shell.v'
        with open(file_name, 'r') as file:
            lines = file.readlines()
        new_lines, cmt_flag = [], 0
        for line in lines:
            if line.split('\n')[0] == '`else // CPG_TC_REQ_DRIVER':
                cmt_flag = 1
            elif line.split('\n')[0] == '`endif  // CPG_TC_REQ_DRIVER':
                cmt_flag = 0
            elif cmt_flag == 1:
                line = '//pvtb// ' + line
            new_lines.append(line)
        with open(file_name, 'w') as file:
            file.write(''.join(new_lines))

    def gen_makef(self, target, more):
        makefile_cont = '''all: clean comp run
    
c clean:
	rm -rf simv* csrc vc_hdrs.h ucli.key exec/* 
    
s vcs_compile_pvtb comp:
	./vcs_compile_pvtb.run
    
r verdi_sim_pvtb.run run:
	./verdi_sim_pvtb.run
        '''
        with open(target + 'Makefile', 'w') as f:
            f.write(makefile_cont)
    
    def monitor_delete(self, target, more):
        monitor_define_dir = target + self.project + '/design/misc/define/mut_adjust_virage_defines.v' #unclassify
        with open(monitor_define_dir, 'r') as file:
            lines = file.readlines()
        filtered_lines = [line for line in lines if not line.rstrip().endswith('_MONITOR')]
        
        filtered_lines_new = []
        #with open(monitor_define_dir, 'r') as file:
        #    lines = file.readlines()
        for line in filtered_lines:
            found = False
            for item in self.rtl2shell_def_list:
                if '`define ' + item.upper() + '_RTL' == line.strip():
                    if any(i == item for i in ['cp', 'cpc']):
                        line = '`define PVTB_' + item.upper() + '_SHELL\n'
                        filtered_lines_new.append(line)
                        found = True
                        break
                    else:
                        line = '`define ' + item.upper() + '_SHELL\n'
                        filtered_lines_new.append(line)
                        found = True
                        break
                elif '`define ABV' == line.strip():
                    found = True
            if not found:
                filtered_lines_new.append(line)
        filtered_lines_new.append('`define MONITOR_SQ_INST_TRACE_MONITOR\n`define MONITOR_SPI_SQ_TRACE_MONITOR\n`define MONITOR_SP_RTL_TRACE_MONITOR\n')
        with open(monitor_define_dir, 'w') as file:
            file.writelines(filtered_lines_new)

    def rm_tree_dir(self, target):
        try:
            shutil.rmtree(target)
        except:
            pass

    def rm_one_file(self, file_dir):
        try:
            os.remove(file_dir)
        except:
            pass
        
    def copy_one_file(self, src_dir, target_dir):
        try:
            shutil.copy2(src_dir, target_dir)
        except:
            pass

    def copy_config_id(self, src_dir, target):
        self.copy_one_file(src_dir + '/../configuration_id', target)

    def change_pvtb_env(self, target, more):
        with open(target + self.project + '/ptb/env_dir.sh', 'r') as enf:
            enf_line = enf.readlines()
        first_line = 'setenv STEM ' + target + '\n'
        enf_line[0] = first_line
        with open(target + self.project + '/ptb/env_dir.sh', 'w') as enf:
            enf.write(''.join(enf_line))
    
    def cpc_shell_maintain(self, src_dir, target):
        ##self.rm_one_file(target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cpc_shell.v')
        self.copy_one_file(src_dir + '/../../maintain_files/cpc_shell.v', target + self.project + '/design/shell/')

    def print_maintain(self, src_dir, target):
        print('Total Files: ' + str(self.copy))
        #print('Skip files: ' + str(self.skip))
        tree_name = target.split('/')[-2]
        print(f'The Tree {tree_name} Build Successed') 
    
    def write_all_copy_files(self, target):
        incdir_all_flist = target + "logs/incdir_all_filelist.xf"  # total copy files
        with open(incdir_all_flist, 'w') as incf:
            for k, v in self.all_files.items():
                incf.write(''.join(v) + '\n')

    def get_git(self, target, key, one_git, more):
        ##git_cmd = 'git clone git@gitlab:archpv/pvtb.git'
        git_cmd = 'git clone --depth 1 git@gitlab:archpv/' + one_git + '.git'
        try:
            child = pexpect.spawn(git_cmd, cwd = target)
            index = child.expect(["Enter passphrase for key", pexpect.EOF, pexpect.TIMEOUT], timeout = 120)
            ### if matched pass key string, index == 0
            if index == 0:
                if key:
                    password_key = key
                else:
                    password_key = getpass.getpass("Please input your git password:")
                child.sendline(password_key)
                new_index = child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout = 1200)
                ##child.sendline('your_password')
                if new_index == 0:
                    output = child.before.decode('utf-8')
                    if 'Checking out' in output and 'done' in output:
                        print(one_git + ' Clone Successed!')
                    elif 'fatal:' in output or 'error:' in output:
                        print(one_git + ' Clone Failed')
                else:
                    print(one_git + ' Clone Timeout')
            elif index == 1:
                print(one_git + ' Clone Successed!')
            elif index == 2:
                print(one_git + ' Clone Timeout')
        except :
            print(one_git + ' Clone Failed!')
    
    def gen_git(self, target, key, more):
        git_total = ['pvtb'] #, 'gkt', 'psm', 'design']
        for one_git in git_total:
            self.rm_tree_dir(target + self.project + one_git)
            self.get_git(target + self.project, key, one_git, more)
        ##os.chdir(target + self.project)
        ##result = subprocess.run(["mv", "pvtb/", "ptb/"], capture_output = True, text = True)
            

    def original_flist(self, target, ngtb_flist, ngtb_all_cmt_flist, ngtb_rtl_cmt_flist, rtl_target, old_few_incdir, more):
        self.flist_delete_cmt(target, ngtb_flist, ngtb_all_cmt_flist, rtl_target, more)
        rtl_orig_flist_for_cp = self.flist_for_copy(ngtb_flist, ngtb_rtl_cmt_flist, old_few_incdir, more)
    
    def reduce_append_to_last_rtl_flist(self, ngtb_base_dir, target, ngtb_all_cmt_flist, ngtb_rtl_cmt_flist, last_rtl_copy_flist, last_all_copy_flist, reduced_flist, appended_flist, only_rtl_flist, only_comment_v_flist, more):
        self.flist_change_shell(ngtb_base_dir, target, ngtb_rtl_cmt_flist, last_rtl_copy_flist, reduced_flist, appended_flist, more)
        self.flist_change_shell(ngtb_base_dir, target, ngtb_all_cmt_flist, last_all_copy_flist, reduced_flist, appended_flist, more)
        self.flist_cmt_sub_module(target, last_rtl_copy_flist, reduced_flist)
        self.flist_cmt_sub_module(target, last_all_copy_flist, reduced_flist)
        #self.only_get_rtl_and_cmt_flist(target, last_all_copy_flist, only_rtl_flist, only_comment_v_flist)
        ##self.appended_files_from_source_to_flist(ngtb_base_dir, ngtb_all_cmt_flist, last_all_copy_flist)
        
    def last_mpp_for_copy_flist(self, ngtb_base_dir, target, ngtb_all_cmt_flist, ngtb_rtl_cmt_flist, last_rtl_copy_flist, last_all_copy_flist, last_all_mpp_flist, last_rtl_mpp_flist, appended_flist, reduced_flist, incdir_all_flist, include_all_flist, include_mpp_flist, old_few_incdir, more):
        self.mpp_path_flist(last_rtl_copy_flist, last_rtl_mpp_flist, target, reduced_flist, incdir_all_flist, more)
        self.mpp_path_flist(include_all_flist, include_mpp_flist, target, reduced_flist, incdir_all_flist, more)
        #self.mpp_path_flist(last_all_copy_flist, last_all_mpp_flist, target, reduced_flist, incdir_all_flist, more)
        self.tab_flist_only_copy(ngtb_base_dir, target, appended_flist, more)
        self.relative_include_copy(target)
        self.cpc_shell_maintain(ngtb_base_dir, target) # first: get cpc_shell, for find include
        self.ngtb_v_inc_only_copy(target, last_all_copy_flist,  ngtb_base_dir)
        self.change_path2stem(last_rtl_mpp_flist, target, more)
        self.change_path2stem(include_mpp_flist, target, more)
        #self.change_path2stem(last_all_mpp_flist, target, more)
        self.gen_rtl_f(target, last_rtl_mpp_flist, include_mpp_flist, old_few_incdir)
    
    def get_flist(self, ngtb_base_dir, target, ngtb_flist, rtl_target, more):
        self.create_folder(target)
        os.makedirs(target + '/logs', exist_ok = True)
        old_few_incdir = target + "logs/old_few_incdir_filelist.xf"
        incdir_all_flist = target + "logs/incdir_all_filelist.xf"  # total copy files
        ngtb_all_cmt_flist = target + "logs/ngtb_comment_compfiles_filelist.xf"
        ngtb_rtl_cmt_flist = target + "logs/ngtb_comment_rtl_filelist.xf"
        reduced_flist = target + "logs/reduce_filelist.xf"
        appended_flist = target + "logs/appended_filelist.xf"
        last_rtl_copy_flist = target + "logs/last_rtl_filelist_copy.xf"
        last_all_copy_flist = target + "logs/last_all_filelist_copy.xf"
        last_rtl_mpp_flist = target + "logs/last_rtl_filelist_mapping.xf"
        last_all_mpp_flist = target + "logs/last_all_filelist_mapping.xf"
        only_rtl_flist = target + "logs/only_rtl_flist_out.xf"
        only_comment_v_flist = target + "logs/only_comment_v_flist_out.xf"
        self.original_flist(target, ngtb_flist, ngtb_all_cmt_flist, ngtb_rtl_cmt_flist, rtl_target, old_few_incdir, more)
        self.reduce_append_to_last_rtl_flist(ngtb_base_dir, target, ngtb_all_cmt_flist, ngtb_rtl_cmt_flist, last_rtl_copy_flist, last_all_copy_flist, reduced_flist, appended_flist, only_rtl_flist, only_comment_v_flist, more)
        include_all_flist = target + "logs/incdir_all_flist.xf"   # ngtb source file list
        include_mpp_flist = target + "logs/incdir_all_mpp_flist.xf"  # ptb mapping file list
        self.get_include_file(target, last_all_copy_flist, include_all_flist, ngtb_base_dir)
        self.last_mpp_for_copy_flist(ngtb_base_dir, target, ngtb_all_cmt_flist, ngtb_rtl_cmt_flist, last_rtl_copy_flist, last_all_copy_flist, last_all_mpp_flist, last_rtl_mpp_flist, appended_flist, reduced_flist, incdir_all_flist, include_all_flist, include_mpp_flist, old_few_incdir, more)
        self.cpc_shell_maintain(ngtb_base_dir, target) # second: because overwitten by original file, so copy again


    def shell_config(self, target, more):
        self.monitor_delete(target, more)
        self.maintain_file2shell(target, more)
        self.file_replace_lines(target, more)
        self.file_cmt_lines(target, more)

    def details_maintain(self, target, ngtb_base_dir, more):
        ###self.gen_makef(target, more)
        self.copy_config_id(ngtb_base_dir, target)
        self.print_maintain(ngtb_base_dir, target)
        self.write_all_copy_files(target)
        #self.change_pvtb_env(target, more)

    def exec_func_precise(self, ngtb_base_dir, flist, target, fold, key, more=True):
        rtl_target = target + 'src/rtl/' if target.endswith('/') else target + '/src/rtl/'
        target = target if target.endswith('/') else target + '/'
        self.gen_git(target, key, more)
        self.get_flist(ngtb_base_dir, target, flist, rtl_target, more )
        self.shell_config(target, more)
        self.details_maintain(target, ngtb_base_dir, more) 

    def option_parser(self, type=None):
        parser = argparse.ArgumentParser(description='Copy files from flist ', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-f', '--flist', default= None, dest= 'flist',  help= 'Input a file with your flist in it. For example: /your/flist/path/flist.f')
        parser.add_argument('-t', '--target', default= None, dest= 'target',  help= 'Your target path for copy file. For example: /your/file/path/' )
        parser.add_argument('-k', '--key', default = None, dest = 'key', help= 'Input your gitlab key if you use this option' )
        parser.add_argument('--fold', action = 'store_true', help= 'fold all file in the same direction' )
        parser.add_argument('--more', action = 'store_true', help= 'more detail file to generate' )
        options = parser.parse_args() 
        return options
    
    def get_flist_dir(self):
        sanity_tree_dir = '/project/hawaii/a0/arch/archpv/'
        compfiles_xf = '/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
        #with open(sanity_tree_dir + 'pvtb_sanity_tree/sanity_status', 'r') as file:
        #    sanity_status = file.read()
        #if sanity_status.strip() == '0':
        #    flist_dir = sanity_tree_dir + 'pvtb_sanity_tree/' + compfiles_xf
        #    ngtb_base_dir = sanity_tree_dir + 'pvtb_sanity_tree/'
        #else:
        #    flist_dir = sanity_tree_dir + 'pvtb_sanity_tree_backup/' + compfiles_xf
        #    ngtb_base_dir = sanity_tree_dir + 'pvtb_sanity_tree_backup/'
        flist_dir = sanity_tree_dir + 'ptb_sanity_tree/out.' + self.get_now('ymd', True) + compfiles_xf
        ngtb_base_dir = sanity_tree_dir + 'ptb_sanity_tree/out.' + self.get_now('ymd', True) + '/'
        return flist_dir, ngtb_base_dir


if __name__ == "__main__":
    pt = PVTBTree()
    opt = pt.option_parser()
    flist_dir, ngtb_base_dir = pt.get_flist_dir()
    flist = opt.flist or flist_dir
    #flist = '/project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/out.2025-09-08/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
    #ngtb_base_dir = '/project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/out.2025-09-08/'
    #flist = '/project/hawaii/a0/arch/archpv/ptb_sanity_tree/out.2025-09-08/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
    #ngtb_base_dir = '/project/hawaii/a0/arch/archpv/ptb_sanity_tree/out.2025-09-08/'
    start_time = time.time()
    pt.exec_func_precise(ngtb_base_dir, flist, opt.target, opt.fold, opt.key, opt.more)
    use_time = time.time() - start_time
    print(f"Use Time: {use_time / 60:4f} mins")
    


