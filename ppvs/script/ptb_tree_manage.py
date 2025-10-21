#!/usr/bin/env /tools/ctools/rh7.9/anaconda3/2023.03/bin/python3
# -*- coding: utf-8 -*-
"""
@Describe: Create PVTB Tree
@Author: Guo Shihao
Data: 2025.04.27
"""

import os, re, sys, time, stat, pdb, shutil, argparse, pexpect, getpass, time, subprocess
cdir = os.path.dirname(os.path.realpath(__file__)) + '/'

class PVTBManage():
    def __init__(self):
        #self.key_list = ['asfd3281764', 'Password!1q2w', 'Password#3e4r', 'Password%5t6y', 'Password&7u8i', 'Password(9o0p']
        self.key_list = os.getenv('PASSWORD_LIST', 'Password!1q2w,Password#3e4r,Password%5t6y,Password&7u8i,Password(9o0p').split(',')
        self.client_info = {
                'Client name' : 'regressbotpv_pvtb_sanity_tree_alterable',
                'Client host' : 'perforceserver.higon.com',
                'Client root' : '/project/hawaii/a0/arch/archpv/pvtb_sanity_tree_alterable',
                'Server address' : 'perforceserver.higon.com:1666'

                }
        self.static_source_dir = '/project/bowen/b0/arch/arch_pv_psm/liangyu/pvtb_golden_20250526/'

    def filelist_for_copy(self, filelist, cp_out_filelist, more):
        with open(filelist, 'r') as f:
            lines = f.readlines()
        ## For copy file
        cleaned_lines = [line.split('//')[0].lstrip('-v').strip() for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('+')]
        if more:
            with open(cp_out_filelist, 'w') as f:
                f.write('\n'.join(cleaned_lines))
        return cleaned_lines
    
    def copy_all_files(self, tab_dir, target_dir, more):
        s_sum, c_sum, e_sum = 0, 0, 0
        os.makedirs(target_dir, exist_ok = True)
        copied, skipped, errors = self.copy_one_path(tab_dir, target_dir, more)
        c_sum += copied
        s_sum += skipped
        e_sum += errors
        print("    - out copied files: {}".format(c_sum))
        print("    - out skipped files: {}".format(s_sum))
        if more: print("    - out copied error files: %s" % e_sum)
    
    def copy_one_path(self, src_dir, tar_dir, more):
        copied, skipped, errors = 0, 0, 0
        for root, dirs, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            dest_dir_path = os.path.join(tar_dir, rel_path)
            if root.split('/')[-1] == 'tmpcomp':
                os.makedirs(dest_dir_path, exist_ok = True)
                self.copy_tab(src_dir, tar_dir, more)
            elif 'tmpcomp' in root and root.split('/')[-1] != 'tmpcomp' :
                continue
            elif 'pub/sim' in root and root.split('/')[-1] != 'fake_v_incl':
                continue
            else:
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
        return copied, skipped, errors
    
    def copy_tab(self, tab_dir, target, more):
        s_sum, c_sum, e_sum = 0, 0, 0
        src_dir = tab_dir + '/tmpcomp' 
        tab_target = target + '/tmpcomp'
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
            'libsp3.so',
            'libsp3_disasmble.so',
            'libsh_meta.so',
            'libdummy_sc_main.so'
            ]
        for root, dirs, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            dest_dir_path = os.path.join(tab_target, rel_path)
            for file in pvtb_tab_file_list:
                if file in files:
                    os.makedirs(dest_dir_path, exist_ok = True)
                    try:
                        shutil.copy2(src_dir + '/' + file, tab_target)
                    except:
                        pass
        try:
            shutil.rmtree(target + '/tmpcomp/sim')
        except:
            pass
        if more:
            for dir in tab_dir_list:
                tab_dir_ = tab_dir + dir 
                skipped, copied, errors = self.copy_one_path(tab_dir_, tab_target, more)
                s_sum += skipped
                c_sum += copied
                e_sum += copied
            print("    - tab copied files: {}".format(c_sum))
            print("    - tab skipped files: {}".format(s_sum))
            print("    - tab copied error files: %s" % e_sum)
    
    def change_path2stem(self, cleaned_filename, target, more):
        #tree_name = target.split('/')[-2]
        #ptn = re.compile('/project[\w/-]+' + tree_name)
        with open(cleaned_filename + '_bwc', 'r') as infile, \
             open(target + 'pvtb/rtl.f', 'w') as outfile:
            for line in infile:
                #modified_line = ptn.sub('$STEM', line)
                outfile.write(line)

    def files_replace(self, src_dir, tar_dir, more):
        


        pass

    def get_git_pull(self, target, key, more):
        target = target + 'pvtb'
        git_cmd = 'git pull'
        try:
            child = pexpect.spawn(git_cmd, cwd = target)
            index = child.expect(["Enter passphrase for key", pexpect.EOF, pexpect.TIMEOUT], timeout = 60)
            ### if matched pass key string, index == 0
            if index == 0:
                if key:
                    password_key = key
                else:
                    password_key = getpass.getpass("Please input your git password:")
                child.sendline(password_key)
                new_index = child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout = 60)
                #child.sendline('your_password')
                if new_index == 0:
                    output = child.before.decode('utf-8')
                    if 'Checking out' in output and 'done' in output:
                        print('Pull Successed!')
                    elif 'fatal:' in output or 'error:' in output:
                        print('Pull Failed')
                else:
                    print('Pull Timeout')
            elif index == 1:
                print('Pull Successed!')
            elif index == 2:
                print('Pull Timeout')
        except :
            print('Pull Failed!')
    
    def get_git_clone(self, target, key, more):
        git_cmd = 'git clone --depth 1 git@gitlab:archpv/pvtb.git'
        try:
            child = pexpect.spawn(git_cmd, cwd = target)
            index = child.expect(["Enter passphrase for key", pexpect.EOF, pexpect.TIMEOUT], timeout = 180)
            ### if matched pass key string, index == 0
            if index == 0:
                if key:
                    password_key = key
                else:
                    password_key = getpass.getpass("Please input your git password:")
                child.sendline(password_key)
                new_index = child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout = 900)
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
        
    def alterable_copy(self, target, shelve_file):
                #if os.path.exists(dst_file) and not overwrite:
                #    skipped += 1
                #    continue
        pass

    def login_regressbotpv(self, target, key_list, sync_tree_dir, more):
        try:
            for password in key_list:
                try:
                    logfile = open(target + '/sync_files.log', 'wb')
                    child = pexpect.spawn('/tool/pandora/bin/tcsh')
                    child.logfile = logfile
                    #child = pexpect.spawn(f'su - regressbotpv', timeout = 8)
                    child.sendline('su regressbotpv')
                    child.expect('Password:')
                    child.sendline(password)
                    #child.expect(f'Last Login:')
                    child.expect(f'\n')
                    child.sendline(f'cd /project/hawaii/a0/arch/archpv/pvtb_sanity_tree_alterable')
                    #child.expect(f'\n')
                    child.sendline('setenv P4CONFIG P4CONFIG')
                    #child.expect(f'\n')
                    child.sendline(f'p4 info')
                    #child.expect(f'Case')
                    child.sendline(f'p4 changes -m 2')
                    child.expect(f'Change')
                    output = child.before.decode()
                    #print(output)
                    break
                except pexpect.exceptions.EOF:
                    #print(f'Failed with password: {password}')
                    continue
            else:
                pass
                #print('All password attempts failed.')
        except:
            pass
        return child
    
    def change_pvtb_env(self, target, more):
        with open(target + 'pvtb/env_dir.sh', 'r') as enf:
            enf_line = enf.readlines()
        first_line = 'setenv STEM ' + target + '\n'
        enf_line[0] = first_line
        with open(target + 'pvtb/env_dir.sh', 'w') as enf:
            enf.write(''.join(enf_line))

    def copy_static_source_dir(self, static_source_dir, target, more):
        src_dir = static_source_dir + 'src'
        copied, skipped, errors = self.copy_one_path(src_dir, target + 'src', more)
        #import_dir = static_source_dir + 'import'
        #copied, skipped, errors = self.copy_one_path(import_dir, target + 'import', more)

    def rm_one_file(self, target):
        try:
            os.remove(target)
        except:
            pass

    def update_file_copy(self, update_file, target):
        for file in update_file:
            src_file = file.split(' ')[-1].split()[0]
            target_path = target + 'src/rtl/'
            self.rm_one_file(target_path + file)
            os.makedirs(target_path, exist_ok = True)
            try:
                shutil.copy2(src_file, target_path)
            except:
                pass
    
    def copy_one_file(self, src_dir, target_dir):
        try:
            shutil.copy2(src_dir, target_dir)
        except:
            pass

    def search_sync_files(self, output, more):
        matches = []
        ptn = r'/project.*?(?=\r\n)'
        output_ = output.split(' ')
        for file in output_:
            match = re.search(ptn, file)
            if match:
                matches.append(match.group())
        if more: print(matches)
        return matches

    def search_unshelve_files(self, target, sync_tree_dir, output, more):
        matches = []
        ptn = r'/(?=dcu).*?(?=#)'
        output_ = output.split(' ')
        for file in output_:
            match = re.search(ptn, file)
            if match:
                depot_file = match.group()
                relative_file_dir = '/'.join(depot_file.split('/')[6:])
                matches.append(sync_tree_dir + relative_file_dir)
        if more: print(matches)
        return matches

    def copy_sync_files(self, source_matches, target, more):
        for src_file in source_matches:
            file = src_file.split('/')[-1]
            self.rm_one_file(target + '/' + file)
            self.copy_one_file(src_file, target)
    
    def copy_config_id(self, src_dir, target):
        self.copy_one_file(src_dir + 'configuration_id', target)
    
    def copy_maintain_files(self, src_dir, target):
        self.copy_one_file(src_dir + '../maintain_files/cpc_shell.v', target + 'src/vega20c/common/pub/src/rtl/bia_ifrit_logical/')
        #self.copy_one_file(src_dir + '../maintain_files/rtl.f', target + 'pvtb/')

    def sync_changelist(self, target, sync_tree_dir, changelist_num, more):
        with open(sync_tree_dir + 'sync_flag', 'r') as f:
            sync_status = f.read().strip()
            if sync_status == '0':
                with open(sync_tree_dir + 'sync_flag', 'w') as f:
                    f.write('1')
                try:
                    with open(target + '/configuration_id') as f:
                        cfg_id = f.readlines()[0]
                except:
                    print('First Step: apy pvtb_tree_manage.py -t ' + target)
                    print('Second Step: apy pvtb_tree_manage.py -t ' + target + ' -cl ' + changelist_num + '\n      Thanks!')
                    with open(sync_tree_dir + 'sync_flag', 'w') as f:
                        f.write('0')
                    sys.exit()
                os.chdir(sync_tree_dir)
                child = self.login_regressbotpv(target, self.key_list, sync_tree_dir, more)
                #with open(sync_tree_dir + 'configuation_id', 'r') as f:
                #    configuation_id_cont = f.read().strip()
                try:
                    child.sendline(f'p4 sync @' + cfg_id)
                    child.expect(f'archpv/pvtb_sanity_tree_alterable>$', timeout = 30)
                    #child.sendline(f'p4 sync @' + configuation_id_cont)
                    #child.expect(f'dcu')
                    child.sendline(f'p4 sync @' + changelist_num)
                    child.expect(f'archpv/pvtb_sanity_tree_alterable>$', timeout = 30)
                    output = child.before.decode()
                    copy_files = self.search_sync_files(output, more)
                    self.copy_sync_files(copy_files, target + '/src/rtl', more)
                except pexpect.exceptions.TIMEOUT as e:
                    print(e)
                child.sendline(f'whoami')
                child.expect(f'regressbotpv')
                #output = child.before.decode()
                #update_file_ = output.split('\n')
                #update_file = [file for file in update_file_ if file != '']
                #self.update_file_copy(update_file, target)
                child.sendline(f'p4 sync ...')
                child.expect(f'archpv/pvtb_sanity_tree_alterable>$', timeout = 30)
                child.close()
            else:
                time.sleep(10)
                self.sync_changelist(target, sync_tree_dir, changelist_num, more)
            with open(sync_tree_dir + 'sync_flag', 'w') as f:
                f.write('0')

    def sync_shelve(self, target, sync_tree_dir, shelve_num, more):
        with open(sync_tree_dir + 'sync_flag', 'r') as f:
            sync_status = f.read().strip()
            if sync_status == '0':
                with open(sync_tree_dir + 'sync_flag', 'w') as f:
                    f.write('1')
                os.chdir(sync_tree_dir)
                child = self.login_regressbotpv(target, self.key_list, sync_tree_dir, more)
                try:
                    child.sendline(f'p4 unshelve -s ' + shelve_num)
                    child.expect(f'archpv/pvtb_sanity_tree_alterable>$', timeout = 30)
                    output = child.before.decode()
                    copy_files = self.search_unshelve_files(target, sync_tree_dir, output, more)
                    self.copy_sync_files(copy_files, target + '/src/rtl', more)
                except pexpect.exceptions.TIMEOUT as e:
                    print(e)
                child.sendline(f'whoami')
                child.expect(f'regressbotpv')
                child.sendline(f'p4 revert ...')
                child.expect(f'archpv/pvtb_sanity_tree_alterable>$', timeout = 30)
                child.close()
            else:
                time.sleep(10)
                self.sync_shelve(target, sync_tree_dir, shelve_num, more)
            with open(sync_tree_dir + 'sync_flag', 'w') as f:
                f.write('0')
        
    def copy_file_update(self, file_update, target, more):
        with open(file_update, 'r') as f:
            upd_file = f.readlines()
        for file in upd_file:
            try:
                file_name = file.split('/')[-1].strip()
                self.rm_one_file(target + '/src/rtl/' + file_name)
                shutil.copy2(file.strip(), target + '/src/rtl')
            except:
                print(f'{file} Copy Failed! Please Copy Manually.')

    def gen_git(self, target, key, more):
        self.get_git_pull(target, key, more)

    def exec_func(self, tab_dir, filelist, target, key, changelist_num, shelve_num, sync_tree_dir, file_update, more=True):
        if changelist_num:
            if target == None:
                cl_target = cdir
            else:
                cl_target = target
            self.sync_changelist(cl_target, sync_tree_dir, changelist_num, more)
            sys.exit()
        if shelve_num:
            if target == None:
                sh_target = cdir
            else:
                sh_target = target
            self.sync_shelve(sh_target, sync_tree_dir, shelve_num, more)
            sys.exit()
        if file_update != None:
            self.copy_file_update(file_update, target, more)
            sys.exit()
        target = target if target.endswith('/') else target + '/'
        self.copy_static_source_dir(tab_dir, target, more)
        ###self.gen_git(target, key, more)
        if not (os.path.isdir(target + 'pvtb') and os.path.exists(target + 'pvtb')):
            self.get_git_clone(target, key, more)
        self.change_pvtb_env(target, more)
        self.change_path2stem(tab_dir + 'from_timescale.compfiles.xf', target, more)
        self.files_replace(tab_dir, target, more)
        self.copy_config_id(tab_dir, target)
        self.copy_maintain_files(tab_dir, target)
        if more:
            self.copy_all_files(tab_dir, target, more)
    
    def exec_func_static(self, static_source_dir, filelist, target, key, changelist_num, shelve_num, sync_tree_dir, more=True):
        target = target if target.endswith('/') else target + '/'
        self.copy_static_source_dir(static_source_dir, target, more)
        self.get_git_clone(target, key, more)
        self.change_pvtb_env(target, more)

def option_parser(type=None):
    parser = argparse.ArgumentParser(description='Copy files from filelist ', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-cl', '--changelist', default= None, dest= 'changelist_num',  help= 'Sync the latest version of rtl')
    parser.add_argument('-sl', '--shelve', default= None, dest= 'shelve_num',  help= 'Sync versions to the specified shelve number')
    parser.add_argument('-t', '--target', default= None, dest= 'target',  help= 'Your target path for copy file. For example: /your/file/path/' )
    parser.add_argument('-k', '--key', default = None, dest = 'key', help= 'Input your gitlab key if you use this option' )
    parser.add_argument('-f', '--file_update', default = None, dest = 'file_update', help= 'Specify the rtl filelist you want to update' )
    parser.add_argument('--more', action = 'store_true', help= 'More detail file to generate' )
    parser.add_argument('--new', action = 'store_true', help= 'Build tree with new rtl' )
    options = parser.parse_args()  
    return options

def get_filelist_dir(new):
    sanity_tree_dir = '/project/hawaii/a0/arch/archpv/'
    compfiles_xf = 'out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
    if new:
        with open(sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/configuration_id', 'r') as f1:
            f1_id = f1.read().strip()
        with open(sanity_tree_dir + 'tree2forcp_pvtb_sanity_tree/configuration_id', 'r') as f2:
            f2_id = f2.read().strip()
        if int(f1_id) > int(f2_id):
            filelist_dir = sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/' + compfiles_xf
            tab_dir = sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/'
        else:
            filelist_dir = sanity_tree_dir + 'tree2forcp_pvtb_sanity_tree/' + compfiles_xf
            tab_dir = sanity_tree_dir + 'tree2forcp_pvtb_sanity_tree/'
    else:
        with open(sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/simulation_sanity_status', 'r') as file:
            tree1_sanity_status = file.read().strip()
        with open(sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/whether_run_flag', 'r') as file:
            tree1_run_status = file.read().strip()
        with open(sanity_tree_dir + 'tree2forcp_pvtb_sanity_tree/simulation_sanity_status', 'r') as file:
            tree2_sanity_status = file.read().strip()
        if tree1_sanity_status == '0' and tree1_run_status == 'had_run':
            filelist_dir = sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/' + compfiles_xf
            tab_dir = sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/'
        elif tree1_sanity_status == '0' and tree1_run_status.strip() == 'have_not_run' and tree2_sanity_status == '1':
            filelist_dir = sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/' + compfiles_xf
            tab_dir = sanity_tree_dir + 'tree1forcp_pvtb_sanity_tree/'
        else:
            filelist_dir = sanity_tree_dir + 'tree2forcp_pvtb_sanity_tree/' + compfiles_xf
            tab_dir = sanity_tree_dir + 'tree2forcp_pvtb_sanity_tree/'
    return filelist_dir, tab_dir


if __name__ == "__main__":
    opt = option_parser()
    filelist_dir, tab_dir = get_filelist_dir(opt.new)
    sync_tree_dir = '/project/hawaii/a0/arch/archpv/pvtb_sanity_tree_alterable/'
    pt = PVTBManage()
    #filelist_dir = '/project/hawaii/a0/arch/guoshihao/bwc_0310/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/from_timescale.compfiles.xf'
    #tab_dir = '/project/hawaii/a0/arch/guoshihao/bwc_0408/'
    static_source_dir = pt.static_source_dir
    #pt.exec_func_static(static_source_dir, filelist_dir, opt.target, opt.key, opt.changelist_num, opt.shelve_num, sync_tree_dir, opt.more)
    pt.exec_func(tab_dir, filelist_dir, opt.target, opt.key, opt.changelist_num, opt.shelve_num, sync_tree_dir, opt.file_update, opt.more)


