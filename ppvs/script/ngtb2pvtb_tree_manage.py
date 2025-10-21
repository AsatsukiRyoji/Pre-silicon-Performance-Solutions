#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Describe: Create PVTB Tree, NGTB2PVTB
@Author: Guo Shihao
Data: 2025.03.10
"""

import os, re, sys, time, stat, pdb, shutil, argparse, pexpect, getpass
cdir = os.path.dirname(os.path.realpath(__file__)) + '/'

class PVTBTree():
    def __init__(self):
        #self.shell_list = ['cpf', 'cpg', 'cpc', 'dbgu_gfx', 'bpmh', 'gc_cac', 'gds', 'rlc', 'tpi', 'rdft_gc_wrapper', 'gc_internal_monitors', 'sq_monitors', 'utcl2_snoop_monitors']
        self.shell_list = ['cpc', 'cpf', 'rlc', 'cpg', 'bpmh', 'gc_internal_monitors', 'cp', 'core_dumpctrl', 'send_signal_monitor', 'core_trackers', 'gc', 'power_ip', 'dbgu_gfx', 'gc_cac', 'rdft_se_wrapper', 'tpi', 'gfx_dbg_steer_wrapper', 'gfx_dbg_client_oring', 'cpaxi', 'cci' ] #, 'gds' 'sq_monitors',
        #self.shell_sub_module_list = ['cpc_save', 'cpc_mec', 'cpg', 'gc_internal_monitors', 'pwoer_ip', 'core_dumpctrl', 'send_signal_monitor', 'core_trackers', 'sq_monitors', 'power_ip', 'dbgu_gfx', 'gds', 'gc_cac', 'rdft_se_wrapper', 'tpi', 'gfx_dbg_steer_wrapper', 'gfx_dbg_client_oring' ] # can not have some module, because will use these sub-module: bpmh, cp, gc, rlc, cpf
        self.shell_sub_module_list = ['ccim', 'cci', 'cpc_save', 'cpc_mec', 'cpg', 'gc_internal_monitors', 'power_ip', 'core_dumpctrl', 'send_signal_monitor'] #, 'core_trackers', 'sq_monitors', 'power_ip' ] # can not have some module, because will use these sub-module: bpmh, cp, gc, rlc, cpf, 'gds', 
        self.rtl2shell_def_list = ['rlc', 'cpc', 'cpg', 'cpf', 'bpmh', 'gc', 'cp', 'abv']
        self.comment_sv_list = ['rlc.vu.sv', 'cpf.vu.sv', 'cpc.vu.sv', 'cpg.vu.sv'] #, 'sq_monitors_se_sh_cu.sv'
        self.comment_specific_list = ['sdp_if.sv', 'sdp_uvc_pkg.sv', 'sdp_uvc_dpi_pkg.sv', 'amd_axi4_uvc_pkg.sv', 'amd_axi4_if.sv', 'amd_axi4_uvc_dpi_pkg.sv', 'uvmkit_pkg.sv', 'uvmkit_reg_pkg.sv', 'uvm_pkg.sv', 'cpaxi.v', 'cpaxi_common_defines_pkg.sv', 'cpaxi_core.v', 'cpaxi_reset.v']
        self.maint_file_list = ['cp.v', 'gc.v'] #, 'cpc.v', 'cp.v', 
        self.comment_instance = {
            'cp.v' : ['bpm_cpc', 'bpm_cpg', 'bpm_cpf_rep', 'cpaxi', 'cp_rep_Cpl_GFXCLK', 'bpm_cci', 'cci'],
            'cpc.v' : ['perfmon_state_sync', 'u_cpc_dbg_mux0', 'u_cpc_dbg_mux1', 'uccim', 'uccis', 'ucpc_ati_grbm_priv_intf', 'ucpc_cciu', 'ucpc_cg_sync_cpc_cpg', 'ucpc_cgtt_local_1r2d', 'ucpc_mec', 'ucpc_perfmon', 'ucpc_query_unit', 'ucpc_rbiu', 'ucpc_rciu', 'ucpc_reset', 'ucpc_roq_mec1', 'ucpc_roq_mec2', 'ucpc_save', 'ucpc_tciu', 'ucpc_utcl2_decode', 'ucpc_utcl2iu', 'ugfx_ecc_irritator_wrapper_0', 'ugfx_ecc_irritator_wrapper_1', 'ugfx_ecc_irritator_wrapper_2', 'vcpc_vbind'],
            'gc.v' : ['ea']
            }
        self.comment_module = {
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

    def filelist_for_copy(self, filelist, cp_out_filelist, more):
        with open(filelist, 'r') as f:
            lines = f.readlines()
        ## For copy file
        cleaned_lines = [line.split('//')[0].lstrip('-v').strip() for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('+')]
        if more:
            with open(cp_out_filelist, 'w') as f:
                f.write('\n'.join(cleaned_lines))
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

    def change_path2stem(self, cleaned_filename, target, more):
        tree_name = target.split('/')[-2]
        ptn = re.compile('/project[\w/-]+' + tree_name)
        with open(cleaned_filename, 'r') as infile, \
             open(target + 'pvtb/rtl.f', 'w') as outfile, \
             open(cleaned_filename + '_bwc', 'w') as outfile1:
            for line in infile:
                modified_line = ptn.sub('$STEM', line)
                outfile.write(modified_line)
                outfile1.write(modified_line)

    def remove_comments(self, filelist, cp_out_filelist, output_name_path, target_dir, more):
        ## For compile
        ##lines = self.filelist_for_copy(filelist, cp_out_filelist, more)
        with open(filelist, 'r') as f:
            lines = f.readlines()
        update_lines = []
        os.makedirs(target_dir, exist_ok = True)
        with open(output_name_path, 'w') as f:
            comp_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//')]
            for line in comp_lines:
                parts = line.split()
                if 'arch' not in line:
                    f.write(line + '\n')
                    continue
                if '+incdir+' in line:
                    target_dir_ = os.path.normpath(target_dir + '../') + '/'
                    line, src_dir = self.get_incdir_dir(line, target_dir_)
                    f.write('+incdir+' + line + '\n')
                    continue
                if len(parts) < 2:
                    new_file_path = os.path.join(target_dir, os.path.basename(line))
                    f.write(new_file_path + '\n')
                    continue
                option = parts[0]
                file_path = ' '.join(parts[1:])
                new_file_path = os.path.join(target_dir, os.path.basename(file_path))
                f.write("{} {}\n".format(option, new_file_path))
    
    def copy_rtl_files(self, filelist, cp_out_filelist, target_dir, preserve_structure=True, more=True):
        success, skips, errors = 0, 0, 0
        os.makedirs(target_dir, exist_ok = True)
        filelist_cp = self.filelist_for_copy(filelist, cp_out_filelist, more)
        ###with open(cp_out_filelist, 'r') as f:
        ###    files = [line.strip() for line in f.readlines() if line.strip()]
        for src_path in filelist_cp:
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
    
    def copy_incdir_file(self, filelist, target, overwrite, more):
        s_sum, c_sum, e_sum = 0, 0, 0
        out_target = target + 'src/' if target.endswith('/') else target + '/src/'
        with open(filelist, 'r') as f:
            lines = f.readlines()
        incdir_lines = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//') and '+incdir+' in line]
        for line in incdir_lines:
            if 'arch' in line:
                tar_dir, src_dir = self.get_incdir_dir(line, out_target)
                skipped, copied, errors = self.copy_one_path(src_dir, tar_dir, overwrite, more)
            s_sum += skipped
            c_sum += copied
            e_sum += errors
        print("    - out copied files: {}".format(c_sum))
        print("    - out skipped files: {}".format(s_sum))
        if more: print("    - out copied error files: %s" % e_sum)
    
    def create_folder(self, target):
        folder_list = [
                        'import',
                        #'src/methodology',
                        #'src/test',
                        'src/tmpcomp',
                        'out/compile/cache_sanity_test',
                        'out/run/cache_sanity_test'
                        ]
        for dir in folder_list:
            os.makedirs(target + dir, exist_ok = True)
    
    def copy_one_path(self, src_dir, tar_dir, overwrite, more):
        copied, skipped, errors = 0, 0, 0
        for root, dirs, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            dest_dir_path = os.path.join(tar_dir, rel_path)
            os.makedirs(dest_dir_path, exist_ok = True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir_path, file)
                #if os.path.exists(dst_file) and not overwrite:
                #    skipped += 1
                #    continue
                try:
                    self.rm_one_file(dst_file)
                    shutil.copy2(src_file, dst_file)
                    copied+=1
                except Exception as e:
                    #if more: print("Copy fail: {} --> {}".format(src_file, e))
                    errors += 1
        return skipped, copied, errors
    
    def copy_tab(self, tab_dir, target, overwrite, more):
        s_sum, c_sum, e_sum = 0, 0, 0
        tab_target = target + 'src/tmpcomp'
        #tab_dir_list = [
        #        'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2',
        #        'out/linux_3.10.0_64.VCS/common/pub/bin',
        #        'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin',
        #        'out/linux_3.10.0_64.VCS/common/pub/bin/sim/VCS-D-2023.03-SP2-2',
        #        'out/linux_3.10.0_64.VCS/vega20c/common/pub/src/verif/interfaces/sdp_uvc/cxx'
        #        ]
            ### for xcd
        tab_dir_list = [
                #'out/linux_3.10.0_64.VCS/common/pub/bin/../../tmp/toolkit/hyvmt/verif_release_ro/tbhydra_pkg/1.0.7/src/base/mem/memio/c/lib/',
                #'out/linux_3.10.0_64.VCS/common/pub/bin/../../tmp/project/djk3/r2/tibox1/cross-merged-vmt/merged_vmt/basepkg_pkg/1.0.2/src/message/msgio/c/',
                #'out/linux_3.10.0_64.VCS/common/pub/bin/../../tmp/toolkit/hyvmt/verif_release_ro/connectivity_pkg/1.0.5/interface/src/vecio/c/',
                #'out/linux_3.10.0_64.VCS/common/pub/bin/../../tmp/project/djk3/r2/tibox1/cross-merged-vmt/merged_vmt/basepkg_pkg/1.0.2/src/datatypes/quadstate/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../../../../../../../../../../djk3/r2/tibox1/cross-merged-vmt/merged_vmt/basepkg_pkg/1.0.2/src/base/random/pli/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../tmp/project/djk3/r2/tibox1/cross-merged-vmt/merged_vmt/basepkg_pkg/1.0.2/src/base/random/pli/VCS-D-2023.03-SP2-2/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../tmp/toolkit/hyvmt/verif_release_ro/tbhydra_pkg/1.0.7/src/base/mem/memio/pli/VCS-D-2023.03-SP2-2/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../tmp/project/djk3/r2/tibox1/cross-merged-vmt/merged_vmt/basepkg_pkg/1.0.2/src/message/msgio/pli/VCS-D-2023.03-SP2-2/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../tmp/src/verif/sh/tools/cmn/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../tmp/toolkit/hyvmt/verif_release_ro/connectivity_pkg/1.0.5/interface/src/vecio/pli/VCS-D-2023.03-SP2-2/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../../../../../../../../../../../toolkit/hyvmt/verif_release_ro/tbhydra_pkg/1.0.7/src/base/mem/memio/pli/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../../../../../../../../../../djk3/r2/tibox1/cross-merged-vmt/merged_vmt/basepkg_pkg/1.0.2/src/message/msgio/pli/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/sim/VCS-D-2023.03-SP2-2/../../../../../../../../../../../../../../toolkit/hyvmt/verif_release_ro/connectivity_pkg/1.0.5/interface/src/vecio/pli/',
                'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/../../../../../../../src/meta/tools/sp3/bin/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/../../../library/gc-vega20c/tmp/src/meta/tools/sp3/lib/',
                #'out/linux_3.10.0_64.VCS/vega20c/common/pub/bin/../../tmp/src/verif/sh/tools/sh_meta/',
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
        pvtb_tab_file_list = [
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
        for dir in tab_dir_list:
            src_dir = tab_dir + dir 
            for root, dirs, files in os.walk(src_dir):
                rel_path = os.path.relpath(root, src_dir)
                dest_dir_path = os.path.join(tab_target, rel_path)
                for file in pvtb_tab_file_list:
                    if file in files:
                        os.makedirs(dest_dir_path, exist_ok = True)
                        try:
                            self.rm_one_file(tab_target + file)
                            if file == 'libsp3.so.1':
                                shutil.copy2(src_dir + '/' + file, tab_target + '/' + 'libsp3.so')
                            else:
                                shutil.copy2(src_dir + '/' + file, tab_target)
                        except:
                            pass
        self.rm_tree_dir(target + 'src/tmpcomp/sim')
        if more:
            for dir in tab_dir_list:
                tab_dir_ = tab_dir + dir 
                skipped, copied, errors = self.copy_one_path(tab_dir_, tab_target, overwrite, more)
                s_sum += skipped
                c_sum += copied
                e_sum += errors
            print("    - tab copied files: {}".format(c_sum))
            print("    - tab skipped files: {}".format(s_sum))
            print("    - tab copied error files: %s" % e_sum)
    
    def copy_import(self, import_dir, target, overwrite, more):
        #src_dir = import_dir + 'import'
        #tar_dir = target + 'import'
        #skipped, copied, errors = self.copy_one_path(src_dir, tar_dir, overwrite, more)
        #print("    - import copied files: {}".format(copied))
        #print("    - import skipped files: {}".format(skipped))
        #if more: print("    - import copied error files: %s" % errors)
        pass

    def filelist_change_shell(self, target, filename, more):
        with open(filename, 'r') as file:
            lines = file.readlines()
        modified_lines = []
        for line in lines:
            modifier = False
            shell_file_name = line.strip().split('/')[-1]
            for shell_file in self.shell_list:
                shell_related_ptn = r'^' + shell_file + '.*\.'
                if shell_file + '.v' == shell_file_name or shell_file + '.sv' == shell_file_name:
                    modifier = True
                    #new_line = line.replace(shell_file + '.v', shell_file + '_shell.v')
                    if shell_file == 'cp':
                        new_shell_name = 'cp_with_cpg_cpf_cpc.v\n'
                    #elif shell_file == 'cpc':
                    #    new_shell_name = 'cpc_only_dc0.v\n'
                    elif shell_file == 'gc':
                        new_shell_name = 'gc_without_ea.v\n'
                    else:
                        new_shell_name = shell_file + '_shell.v\n'
                    new_line = '//pvtb2shell//' + line + target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/' + new_shell_name
                    modified_lines.append(new_line)
                elif re.search(shell_related_ptn, shell_file_name) and shell_file + '_shell.v' != shell_file_name:
                    #if any(item in line for item in ['cpc_dc', 'cpc_mem', 'cpc_rfp', 'gds_mem']):
                    #    modifier = True
                    #    modified_lines.append(line)
                    #else:
                    #    modifier = True
                    #    modified_lines.append('//pvtb_shell// {}'.format(line))
                    if any(item in line for item in self.comment_sv_list):
                        if shell_file == 'cp':
                            break
                        modifier = True
                        modified_lines.append('//pvtb_shell// {}'.format(line))
                    elif not modifier:
                        modifier = True
                        modified_lines.append(line)
                elif not modifier:
                    modifier = True
                    have_flag = 0
                    for shell_file in self.shell_list:
                        if shell_file + '.v' == shell_file_name or shell_file + '.sv' == shell_file_name or any(item in line for item in self.comment_sv_list):
                            have_flag =1
                            break
                    ### After first string 'cpf', will append twice, this code ensure only generate once
                    #for shell_file in self.shell_list:
                    #    shell_related_ptn = r'^' + shell_file + '.*\.'
                    #    if re.search(shell_related_ptn, shell_file_name) and shell_file + '_shell.v' != shell_file_name:  
                    #        have_flag = 1
                    #        #modified_lines.append(line)
                    #        break
                    if shell_file_name == 'tb_gc.sv':
                        continue
                    elif not have_flag:
                        modifier = True
                        modified_lines.append(line)
        #line_pvtb = target + 'pvtb/pvtb_filelist.compile.bwc.xf\n'
        #line_pvtb = target + 'pvtb/from_timescale.compfiles.bwc.xf\n'
        for vec_file in self.vec_specified_files:
            line_pvtb = target + 'src/rtl/' + vec_file + '\n'
            modified_lines.append(line_pvtb)
        with open(filename, 'w') as file:
            file.writelines(modified_lines)

    def comment_for_specific_file(self, filename, target, more):
        with open(filename, 'r') as file:
            lines = file.readlines()
        modified_lines = []
        for line in lines:
            comment_file_name = line.strip().split('/')[-1]
            for shell_file in self.comment_specific_list:
                if shell_file == comment_file_name:
                    line = '//pvtb_shell// ' + line
            modified_lines.append(line)
        with open(filename, 'w') as file:
            file.writelines(modified_lines)

    def filelist_comment_sub_module(self, target, filename, more):
        with open(filename, 'r') as file:
            lines = file.readlines()
        modified_lines = []
        for line in lines:
            modifier = False
            shell_file_name = line.strip().split('/')[-1]
            for shell_file in self.shell_sub_module_list:
                shell_related_ptn = r'^' + shell_file + '.*\.'
                if re.search(shell_related_ptn, shell_file_name) and shell_file + '_shell.v' != shell_file_name:
                    if any(item in line for item in self.comment_sv_list):
                        modifier = True
                        modified_lines.append(line)
                    elif any(item in line for item in self.shell_sub_module_list):
                        modifier = True
                        modified_lines.append('//pvtb_shell// {}'.format(line))
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
        with open(filename, 'w') as file:
            file.writelines(modified_lines)

    def maintain_file2shell(self, target, more):
        for file in self.maint_file_list:
            with open(target + 'src/rtl/' + file, 'r') as f:
                file_cont = f.readlines()
            define_flag, comment_lines = 0, []
            for line in file_cont:
                if any(item in line for item in self.comment_module[file]) and any(item in line for item in self.comment_instance[file]):
                    define_flag = 1
                    leading_spaces = line[:len(line) - len(line.lstrip())]
                    #if file == 'cp.v':
                    #    line = leading_spaces + '`ifndef PVTB_CP_SHELL\n' + line
                    #elif file == 'cpc.v':
                    #    line = leading_spaces + '`ifndef PVTB_CPC_SHELL\n' + line
                    if file == 'gc.v':
                        line = leading_spaces + '`ifndef PVTB_EA_RTL_OMIT\n' +line
                    comment_lines.append(line)
                elif ');' in line.strip() and define_flag == 1:
                    if file == 'cp.v':
                        comment_lines.append(line)
                        continue
                    define_flag = 0
                    leading_spaces = line[:len(line) - len(line.lstrip())]
                    line += leading_spaces + '`endif\n'
                    comment_lines.append(line)
                elif all(item not in line for item in self.comment_instance[file]):
                    comment_lines.append(line)
                else:
                    comment_lines.append(line)
            if file == 'cp.v':
                with open(target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cp_with_cpg_cpf_cpc.v', 'w') as f:
                    f.write(''.join(comment_lines))
            #elif file == 'cpc.v':
            #    with open(target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cpc_only_dc0.v', 'w') as f:
            #        f.write(''.join(comment_lines))
            elif file == 'gc.v':
                with open(target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/gc_without_ea.v', 'w') as f: 
                    f.write(''.join(comment_lines))

    def file_replace_lines(self, target, more):
        file_name = target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cp_with_cpg_cpf_cpc.v'
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

    def file_comment_lines(self, target, more):
        file_name = target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cpg_shell.v'
        with open(file_name, 'r') as file:
            lines = file.readlines()
        new_lines, comment_flag = [], 0
        for line in lines:
            if line.split('\n')[0] == '`else // CPG_TC_REQ_DRIVER':
                comment_flag = 1
            elif line.split('\n')[0] == '`endif  // CPG_TC_REQ_DRIVER':
                comment_flag = 0
            elif comment_flag == 1:
                line = '//pvtb// ' + line
            new_lines.append(line)
        with open(file_name, 'w') as file:
            file.write(''.join(new_lines))

    def gen_compf(self, target, cleaned_filename, more):
        comp_cont = "bsub -Ip -q regr_high vcs +error+4 -ntb_opts uvm-1.2 -kdb +define+DISABLE_SQC_CACHE_CHECKER -fgp +define+PA_FCOV_ON +define+ABV=0 +define+MC_IP_ABV_FUNC_EN=0 -Xnjoshi=0x10000 -top tb -lca -debug_access+all -debug_region=cell+lib -full64 -assert novpi+dbsopt -Xkeyopt=amd1 -reportstats -l $STEM/out/compile/vcs_compile.log -Mupdate -ld /tools/hydora64/hdk-r7-9.2.0/22.10/bin/g++ +vcs+lic+wait -override_timescale=1ps/1ps -assert svaext +define+COSIM_LIB_UNAVAILABLE -f $STEM/from_timescale.compfiles.xf_bwc -psl -sverilog +vpi +nospecify +notimingchecks +lint=CDOB +lint=PCWM +lint=ERASM +lint=TFIPC +warn=IEELMME +vcs+error=DPIMI +warn=all -P $STEM/src/tmpcomp/msgio.tab -lmsgio_pli -ltt  -P $STEM/src/tmpcomp/vecio.tab -lvecio_pli -P $STEM/src/tmpcomp/memio.tab -lgc_mem_access_api -ltc_cmem_accessor -ltc_l2_ops -lfido -lmemio_pli -laxi4_uvc_dpi -P $STEM/src/tmpcomp/medusa_pli.tab -lmedusa_pli -lhydra_dpi -P $STEM/src/tmpcomp/hydra_pli.tab -lhydra_pli -P $STEM/src/tmpcomp/ati_random.tab -lati_random_pli -lm -laddr_core -lsh_bfm_common_dpi -P $STEM/src/tmpcomp/tb_pli.tab -L$STEM/src/tmpcomp -LDFLAGS -Wl,-rpath,$STEM/src/tmpcomp -ltb_pli -LDFLAGS -ggdb  -lsdp_uvc_dpi"
        
        tab_path = target + 'out/linux_3.10.0_64.VCS/vega20c'
        comp_cont = comp_cont.format(
                cleaned_filename
                )
        with open(target + 'vcs_compile_pvtb.run', 'w') as f:
            f.write(comp_cont)
        os.chmod(target + 'vcs_compile_pvtb.run', 0o755)
    
    def gen_simf(self, target, more):
        sim_cont = "bsub -Ip -q regr_high "
        with open(target + 'verdi_sim_pvtb.run', 'w') as f:
            f.write(sim_cont)
        os.chmod(target + 'verdi_sim_pvtb.run', 0o755)
    
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
    
    def gen_env_sh(self, target, more):
        env_cont = '''setenv STEM {}
module unload vcs
module unload verdi
module load vcs/2020.03-SP2-6
module load verdi/2020.03-SP2-6
        '''
        with open(target + 'env.sh', 'w') as f:
            f.write(env_cont.format(target.rstrip('/')))
        os.chmod(target + 'env.sh', 0o755)

    def monitor_delete(self, target, more):
        monitor_define_dir = target + 'src/rtl/mut_adjust_virage_defines.v'
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
        with open(target + 'pvtb/env_dir.sh', 'r') as enf:
            enf_line = enf.readlines()
        first_line = 'setenv STEM ' + target + '\n'
        enf_line[0] = first_line
        with open(target + 'pvtb/env_dir.sh', 'w') as enf:
            enf.write(''.join(enf_line))

    def copy_maintain_files(self, src_dir, target):
        #self.rm_one_file(target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/cpc_shell.v')
        self.copy_one_file(src_dir + '/../../maintain_files/cpc_shell.v', target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/')
        for spcf_file in self.vec_specified_files:
            self.copy_one_file(src_dir + 'out/linux_3.10.0_64.VCS/vega20c/common/pub/include/interfaces/' + spcf_file, target + 'src/rtl/') 

    def get_git(self, target, key, more):
        git_cmd = 'git clone --depth 1 git@gitlab:archpv/pvtb.git'
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
                #child.sendline('your_password')
                if new_index == 0:
                    output = child.before.decode('utf-8')
                    if 'Checking out' in output and 'done' in output:
                        print('Clone Successed!')
                    elif 'fatal:' in output or 'error:' in output:
                        print('Clone Failed')
                else:
                    print('Clone Timeout')
            elif index == 1:
                print('Clone Successed!')
            elif index == 2:
                print('Clone Timeout')
        except :
            print('Clone Failed!')
        
    def gen_git(self, target, key, more):
        self.rm_tree_dir(target + 'pvtb')
        self.get_git(target, key, more)

    def shell_config(self, target, cleaned_filename, more):
        self.filelist_change_shell(target, cleaned_filename, more)
        self.comment_for_specific_file(cleaned_filename, target, more)
        self.filelist_comment_sub_module(target, cleaned_filename, more)
        self.monitor_delete(target, more)
        self.maintain_file2shell(target, more)
        self.file_replace_lines(target, more)
        self.file_comment_lines(target, more)

    def make_compile(self, target, cleaned_filename, more):
        #self.gen_compf(target, cleaned_filename, more)
        #self.gen_simf(target, more)
        #self.gen_makef(target, more)
        #self.gen_env_sh(target, more)
        #if not more:
        #    self.rm_one_file(target + 'from_timescale.compfiles.xf')
        self.copy_config_id(tab_dir, target)
        self.copy_maintain_files(tab_dir, target)
        self.change_pvtb_env(target, more)

    def exec_func(self, tab_dir, filelist, target, fold, overwrite, key, more=True):
        rtl_target = target + 'src/rtl/' if target.endswith('/') else target + '/src/rtl/'
        target = target if target.endswith('/') else target + '/'
        cleaned_filelist = target + "filelist_copy.xf"
        cleaned_filename = target + "from_timescale.compfiles.xf"
        self.remove_comments(filelist, cleaned_filelist, cleaned_filename, rtl_target, more)
        self.gen_git(target, key, more)
        self.copy_rtl_files( 
                filelist,
                cp_out_filelist = cleaned_filelist,
                target_dir = rtl_target,
                preserve_structure = fold,
                more = False
                )
        self.copy_incdir_file(filelist, target, overwrite, more)
        self.create_folder(target)
        self.copy_tab(tab_dir, target, overwrite, more)
        self.copy_import(tab_dir, target, overwrite, more)
        self.shell_config(target, cleaned_filename, more)
        self.make_compile(target, cleaned_filename, more)
        self.change_path2stem(cleaned_filename, target, more)

    def option_parser(self, type=None):
        parser = argparse.ArgumentParser(description='Copy files from filelist ', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-f', '--filelist', default= None, dest= 'filelist',  help= 'Input a file with your filelist in it. For example: /your/filelist/path/filelist.f' )
        parser.add_argument('-t', '--target', default= None, dest= 'target',  help= 'Your target path for copy file. For example: /your/file/path/' )
        parser.add_argument('-k', '--key', default = None, dest = 'key', help= 'Input your gitlab key if you use this option' )
        parser.add_argument('--fold', action = 'store_true', help= 'fold all file in the same direction' )
        parser.add_argument('--overwrite', action = 'store_true', help= 'overwrite files in the same direction' )
        parser.add_argument('--more', action = 'store_true', help= 'more detail file to generate' )
        options = parser.parse_args()  
        return options
    
    def get_filelist_dir(self):
        sanity_tree_dir = '/project/hawaii/a0/arch/archpv/'
        compfiles_xf = '/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
        #with open(sanity_tree_dir + 'pvtb_sanity_tree/sanity_status', 'r') as file:
        #    sanity_status = file.read()
        #if sanity_status.strip() == '0':
        #    filelist_dir = sanity_tree_dir + 'pvtb_sanity_tree/' + compfiles_xf
        #    tab_dir = sanity_tree_dir + 'pvtb_sanity_tree/'
        #else:
        #    filelist_dir = sanity_tree_dir + 'pvtb_sanity_tree_backup/' + compfiles_xf
        #    tab_dir = sanity_tree_dir + 'pvtb_sanity_tree_backup/'
        filelist_dir = sanity_tree_dir + 'ptb_sanity_tree/out.' + self.get_now('ymd', True) + compfiles_xf
        tab_dir = sanity_tree_dir + 'ptb_sanity_tree/out.' + self.get_now('ymd', True) + '/'
        return filelist_dir, tab_dir


if __name__ == "__main__":
    pt = PVTBTree()
    opt = pt.option_parser()
    filelist_dir, tab_dir = pt.get_filelist_dir()
    filelist = opt.filelist or filelist_dir
    #filelist = '/project/hawaii/a0/arch/archpv/gc_tree_0423/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
    #tab_dir = '/project/hawaii/a0/arch/archpv/gc_tree_0423/'
    #filelist = '/project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
    #tab_dir = '/project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/'
    pt.exec_func(tab_dir, filelist, opt.target, opt.fold, opt.overwrite, opt.key, opt.more)


