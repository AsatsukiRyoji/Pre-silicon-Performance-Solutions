#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enforce sync the tree everyday, and keep a sanity tree
@author: Guo Shihao
Data: 2025.04.17
"""
import os, re, sys, logging, subprocess, time, argparse, pdb, shutil, argparse, pexpect, getpass
from multiprocessing import Process, Lock

logging.basicConfig(filename='/project/hawaii/a0/arch/archpv/tree1forcp_pvtb_sanity_tree/crontab_info.log', level=logging.INFO)
cdir = os.path.dirname(os.path.realpath(__file__)) + '/'

parting_line = '''
###################################
'''
blank_line = '''


'''
### original cmd
#dj_cmd = ('lsf_bsub -Ip -q regr_high dj -c -e 'run_test"perf perf_buffer_load_dwordx4_toLDS_comp1_hitTCC_ipw32_wpg4_so0_tid0"' -m 200 -l /project/hawaii/a0/arch/archpv/%s/logs/perf_buffer_load_dwordx4_toLDS_comp1_hitTCC_ipw32_wpg4.log -DGC_PERF -DSKIP_CAT_EMU_VEC ')
### removed arg: 
dj_cmd = ('/tool/pandora64/bin/lsf_bsub -Ip -q regr_high dj -e \'run_test "cs/cs_sr_sanity_pm4_01"\' -DRUN_GC_SIM -DGFX_CGCG_ENABLE -DGFX_MGCG_ENABLE -DGC_ENABLE_LLVM_SP3 -l /project/hawaii/a0/arch/archpv/%s/logs/cs_sr_sanity_pm4_01.log -DFSDB_RUNTIME_CTRL -DDUMP_WAVE_WITH_LIBFILE -DDUMP_ITRACE -DRUN_DV=OFF') # no need simulation!
pvtb_cmd = ('/project/hawaii/a0/arch/archpv/%s/vcs_compile_pvtb.run')
pvtb_copy_cmd_tree1 = '/tools/ctools/rh7.9/anaconda3/2021.11/bin/python /project/bowen/b0/arch/guoshihao/bowenb0_pv_debug_1101/src/verif/performance/subsystem/util/pvtree_script/ngtb2pvtb_tree_manage.py -t /project/hawaii/a0/arch/archpv/%s'
pvtb_copy_cmd_tree2 = '/tools/ctools/rh7.9/anaconda3/2021.11/bin/python /project/bowen/b0/arch/guoshihao/bowenb0_pv_debug_1101/src/verif/performance/subsystem/util/pvtree_script/ngtb2pvtb_tree_manage.py -t /project/hawaii/a0/arch/archpv/%s --more'
cmd_4sanity = ['command_sanity', 'shader_sanity', 'cache_sanity', 'gemm_sanity']

gc_sanity_tree = 'ptb_sanity_tree'

def option_parser(type=None):
    parser = argparse.ArgumentParser(description='%s options' %type, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--tree', default= 'tree1forcp_pvtb_sanity_tree', dest= 'tree',  help= 'Choose which tree you run')
    parser.add_argument('-k', '--key', default = None, dest = 'key', help= 'Input your gitlab key if you use this option' )
    options = parser.parse_args()  
    return options

def call_from_sys(cmd, has_status=False):
    """Call a command from system.
    Deal different situation per python version
    Return: read handler.
    """
    if (sys.version_info > (3, 0)):
        if has_status == False:
            #py2 subprocess has no this getoutput. 3x can also use 2x way
            output = subprocess.getoutput(cmd)
            return output.split()
        else:
            status, output = subprocess.getstatusoutput(cmd)
            return output.split(), status
            #NOTE|return {'result': output.split(), 'status': status}
    else:
        #A handler as a file reader, can be used only once
        r = subprocess.Popen(cmd, shell= True, stdout= subprocess.PIPE, stderr= open(os.devnull,'w')).stdout
        #NOTE|i is byte string type as b'', need to be decoded to str
        return [i.decode() for i in r.readlines() if i != b'\n']

def get_now(which='dhms', delimiter=False):
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

def ngtb_tree_run(stable_tree):
    os.chdir('/project/hawaii/a0/arch/archpv/' + stable_tree + '/') # change the directory and print the time
    logging.info(parting_line + 'Start at:  ' + get_now('all', True) + parting_line)
    logging.info(os.getcwd())
    #call_from_sys('setenv P4CONFIG P4CONFIG')
    with open('P4CONFIG', 'r') as file:
        for line in file:
            port_name, port_content = line.strip().split('=')
            os.environ[port_name] = port_content
    ### Sync the tree
    logging.info(' ##########  This is sync ... ##########')
    revert_info = subprocess.getoutput('p4 revert ...')  # revert tree
    sync_info = subprocess.getoutput('p4 sync -f ...')  # sync tree
    #try:
    #    out_info = subprocess.getoutput('mv out out.bk')  
    #except:
    #    pass
    edit_makefile_info = subprocess.getoutput('p4 edit src/verif/sh/tools/cmn/Makefile')  
    edit_sh_itrace_info = subprocess.getoutput('p4 edit src/verif/sh/tools/cmn/sh_itrace.cpp')
    #logging.info(sync_info)
    ### Update the changelist
    #call_from_sys('rm -rf /project/hawaii/a0/arch/archpv/'+ stable_tree + '/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/pub/sim/exec/*')
    #call_from_sys('rm -rf /project/hawaii/a0/arch/archpv/'+ stable_tree + '/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/pub/sim/vcs.work/*')
    call_from_sys('mv /project/hawaii/a0/arch/archpv/'+ stable_tree + '/out.* ' + '/project/hawaii/a0/arch/archpv/'+ stable_tree + '/out.last.bak')
    changes = os.popen('p4 changes -m 1').read()
    ptn = r'(Change )(\d+)'
    changelist = re.search(ptn, changes).groups()[1]
    open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/configuration_id','w').write(changelist)
    logging.info('The current changelist is:' + changelist)
    logging.info(' ##########  Sync done ... ##########')
    ### Run dj cmd
    #dj_cmd_info = subprocess.getoutput(dj_cmd)    # rerun the test
    #logging.info(dj_cmd_info)
    logging.info(' ##########  This is GC Compile ##########')
    dj_cmd_new = dj_cmd%(stable_tree)
    result, status = call_from_sys(dj_cmd_new, has_status=True)
    #print(result)
    #with open('/project/hawaii/a0/arch/archpv/' + stable_tree + 'aa.log', 'w') as aa:
    #    aa.write(str(result))
    sanity_status = result[result.index('failed_cmd_count:') + 1]
    #sanity_status = '0'
    if sanity_status == '0':
        if not os.path.isfile('/project/hawaii/a0/arch/archpv/' + stable_tree + '/out.' + get_now('ymd', True) + '/out/linux_3.10.0_64.VCS/vega20c/config/gc/pub/sim/exec/vcs_sim_exe'):
            sanity_status = '1'
    open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/sanity_status', 'w').write(sanity_status)
    logging.info(' ##########  GC Compile status:' + sanity_status)

def change_cmn_makefile(target):
    mf_target = target + gc_sanity_tree + '/src/verif/sh/tools/cmn/Makefile'
    replacement_line = 'LLFLAGS += -L$(OUT_CMN_bin) -lmemio -lsp3 -lsp3_disasmble -lsh_meta\n'
    ptn = r'LLFLAGS'
    with open(mf_target, 'r') as f:
        mf_cont = f.readlines()
    modified = False
    for i, line in enumerate(mf_cont):
        if re.search(ptn, line):
            mf_cont[i] = '#' + line + replacement_line
            modified = True
            break
    with open(mf_target, 'w') as f:
        f.write(''.join(mf_cont))

def change_cmn_itrace(target):
    itc_target = target + gc_sanity_tree + '/src/verif/sh/tools/cmn/sh_itrace.cpp'
    replacement_include = ['#include <medusa.h>', '#include <sysmgr/sysmgr.h>', '#include <sysmgr/filelog.h>']
    with open(itc_target, 'r') as f:
        itc_cont = f.readlines()
    itrace_cont, count_line, begin_flag, end_flag = [], 0, False, False
    for i, line in enumerate(itc_cont):
        if '#include <math.h>' in line:
            itc_cont[i] = line + '#include <string.h>\n#include <stdarg.h>\n'
        for item in replacement_include:
            if item in line:
                itc_cont[i] = '//pvtb//' + line
        if end_flag == False:
            if 'sysmgr data ' in line or begin_flag == True:
                begin_flag = True
                itc_cont[i] = '//pvtb//' + line
                count_line += 1
            if count_line == 18:
                begin_flag = False
                end_flag = True
    with open(itc_target, 'w') as f:
        f.write(''.join(itc_cont))

def after_change_hbo(target):
    with open('logs/auto_pvtb_hbo.log', 'wb') as logfile:
        child = pexpect.spawn('/tool/pandora/bin/tcsh')
        child.logfile = logfile
        os.getcwd()
        try:
            start_time = time.time()
            child.sendline("cd src/verif/sh/tools/cmn/")
            child.expect(r'\n', timeout = 10)
            child.sendline("source /toolkit/hyvmt/verif_release_ro/cbwa_initscript/1.0.0/_init.csh") # This is inicbwa for xcd
            child.expect(r'\n', timeout = 10)
            child.sendline("source /toolkit/hyvmt/verif_release_ro/cbwa_bootcore/$bootcore_ver/bin/_bootenv.csh") # This is bootenv for xcd
            child.expect(r'\n', timeout = 30)
            child.sendline("hbo")
            child.expect(r'passed_cmd_count:', timeout = 1800)
            elapsed_time = time.time() - start_time
            logging.info('      NGTB HBO Total Used Time: ' + str(elapsed_time))
        except pexpect.TIMEOUT:
            logging.info('      NGTB HBO TimeOut~_~')
        except pexpect.EOF:
            logging.info('      NGTB HBO Pass^_^')
        finally:
            if child.isalive():
                child.close()

def ngtb_files_change(target, gc_sanity_tree):
    change_cmn_makefile(target)
    change_cmn_itrace(target)   
    after_change_hbo(target)

def pvtb_tree_run_compile():
    with open('logs/auto_ptb_compile.log', 'wb') as logfile:
        child = pexpect.spawn('/tool/pandora/bin/tcsh')
        child.logfile = logfile
        try:
            start_time = time.time()
            child.sendline("source pvtb/env_dir.sh")
            child.expect(r'\n', timeout = 10)
            child.sendline('echo $STEM')
            child.expect(r'tree', timeout = 5)
            child.sendline('cd out/compile/cache_sanity_test/')
            child.expect(r'\n', timeout = 5)
            child.sendline('rm -rf simv')
            child.expect(r'\n', timeout = 5)
            child.sendline('bsub -W 1:30 -Is ../../../pvtb/ptb_cmd/vcs_compile_psm.run_bwc')
            child.expect(r'CPU time', timeout = 5400) # 1800 = 30 minutes
            elapsed_time = time.time() - start_time
            logging.info('      PVTB Compile Total Used Time: ' + str(elapsed_time))
        except pexpect.TIMEOUT:
            logging.info('      PVTB Compile TimeOut~_~')
        except pexpect.EOF:
            logging.info('      PVTB Compile Pass^_^')
        finally:
            if child.isalive():
                child.close()

def pvtb_tree_run_sim(cmd):
    test_name = cmd.split(' ')[-1].split('/')[-1]
    with open('logs/auto_ptb_simulation_' + test_name + '.log', 'wb') as logfile:
        child = pexpect.spawn('/tool/pandora/bin/tcsh')
        child.logfile = logfile
        try:
            start_time = time.time()
            child.sendline("source pvtb/env_dir.sh")
            child.expect(r'\n', timeout = 10)
            child.sendline('echo $STEM')
            child.expect(r'tree', timeout = 5)
            child.sendline('cd out/run/cache_sanity_test/')
            child.expect(r'\n', timeout = 5)
            #child.sendline('bsub -W 6:00 -Is ../../../pvtb/verdi.local_run_single_dispatch_glbal_load_1tg')
            #child.sendline('bsub -W 6:00 -Is ../../../pvtb/verdi.local_run_single_dispatch_buffer_read_48tg')
            child.sendline(cmd)
            child.expect(r'Simulation Performance Summary', timeout = 18000) # 18000 = 5hour
            elapsed_time = time.time() - start_time
            logging.info('      PVTB Simulation Total Used Time: ' + str(elapsed_time))
        except pexpect.TIMEOUT:
            logging.info('      PVTB Simulation 3 hours')
            #logging.info('      PVTB Simulation TimeOut~_~')
        except pexpect.EOF:
            logging.info('      PVTB Simulation Pass^_^')
        finally:
            if child.isalive():
                child.close()

def pvtb_tree_run_sim_lock(cmd, lock = None):
    with lock:
        print(cmd)
    test_name = cmd.split(' ')[-1].split('/')[-1]
    with open('logs/auto_ptb_simulation_' + test_name + '.log', 'wb') as logfile:
        child = pexpect.spawn('/tool/pandora/bin/tcsh')
        child.logfile = logfile
        try:
            start_time = time.time()
            child.sendline("source pvtb/env_dir.sh")
            child.expect(r'\n', timeout = 10)
            child.sendline('echo $STEM')
            child.expect(r'tree', timeout = 5)
            child.sendline('cd out/run/')
            child.expect(r'\n', timeout = 5)
            #child.sendline('bsub -W 6:00 -Is ../../../pvtb/verdi.local_run_single_dispatch_glbal_load_1tg')
            #child.sendline('bsub -W 6:00 -Is ../../../pvtb/verdi.local_run_single_dispatch_buffer_read_48tg')
            child.sendline(cmd)
            child.expect(r'Simulation Performance Summary', timeout = 10800) # 18000 = 5hour
            elapsed_time = time.time() - start_time
            logging.info('      PTB ' + test_name + ' Simulation Total Used Time: ' + str(elapsed_time))
        except pexpect.TIMEOUT:
            logging.info('      PTB ' + test_name + ' Simulation 3h End ')
        except pexpect.EOF:
            logging.info('      PTB ' + test_name + ' Simulation Pass^_^')
        finally:
            if child.isalive():
                child.close()

def judge_whether_have_file(target, stable_tree):
    folder_path = target + stable_tree + '/out/compile/cache_sanity_test/'
    file_name = 'simv'
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        logging.info('      PVTB Compile Pass')
        open(target + stable_tree + '/compile_sanity_status', 'w').write('0')
    else:
        logging.info('      PVTB Compile Fail')
        open(target + stable_tree + '/compile_sanity_status', 'w').write('1')

def judge_whether_have_str(target, stable_tree, testname):
    sim_flag = 0
    target_file = target + stable_tree + '/out/run/' + testname + '/verdi_run.log'
    with open(target_file, 'r') as readfile:
        file_content = readfile.readlines()
    if 'UVM_ERROR :    0' in str(file_content):
        sim_flag = 0
        logging.info('      PVTB Simulation Pass')
        open(target + stable_tree + '/simulation_sanity_status', 'w').write('0')
    else:
        sim_flag = 1
        logging.info('      PVTB Simulation Fail')
        open(target + stable_tree + '/simulation_sanity_status', 'w').write('1')
    return sim_flag

def pvtb_tree_run(target, stable_tree):
    with open('/project/hawaii/a0/arch/archpv/' + gc_sanity_tree + '/sanity_status', 'r') as f:
        gc_tree_status = f.readlines()[0]
    if gc_tree_status.strip() == '0':
        logging.info(parting_line + 'Start at:  ' + get_now('all', True) + parting_line)
        os.chdir('/project/hawaii/a0/arch/archpv/' + stable_tree + '/') # change the directory and print the time
        logging.info(os.getcwd())
        logging.info(' ##########  This is PVTB Tree Compile  ##########')
        pvtb_tree_run_compile()
        judge_whether_have_file(target, stable_tree)
        logging.info(' ##########  This is PVTB Tree Simulation ##########')
        with open(target + stable_tree + '/compile_sanity_status') as cf:
            compile_status = cf.readlines()[0]
        if compile_status == '0':
            cmd = 'bsub -W 6:00 -Is ../../../pvtb/verdi.local_run_single_dispatch_sanity_48tg'
            pvtb_tree_run_sim(cmd)
            testname = 'cache_sanity_test'
            judge_whether_have_str(target, stable_tree, testname)
            with open(target + stable_tree + '/simulation_sanity_status') as sf:
                simulation_status = sf.readlines()[0]
            if simulation_status == '0':
                open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/whether_run_flag', 'w').write('had_run')
            #env_log = call_from_sys('csh -c "source env.sh"')
            #logging.info('source env.sh log: Null is well:' + str(env_log))
            #pvtb_cmd_new = pvtb_cmd%(stable_tree)
            #result, status = call_from_sys(pvtb_cmd_new, has_status=True)
            #sanity_status = result[result.index('failed_cmd_count:') + 1]
            #open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/sanity_status', 'w').write(sanity_status)
                if stable_tree == 'tree1forcp_pvtb_sanity_tree':
                    open('/project/hawaii/a0/arch/archpv/tree2forcp_pvtb_sanity_tree/whether_run_flag', 'w').write('have_not_run')
                else:
                    open('/project/hawaii/a0/arch/archpv/tree1forcp_pvtb_sanity_tree/whether_run_flag', 'w').write('have_not_run')
        else:
            logging.info('      PVTB Compile Fail, No Simulation ')
            open(target + stable_tree + '/simulation_sanity_status', 'w').write('1')
        logging.info(' ##########  End  ##########')
        logging.info(blank_line)
    else:
        logging.info('Since the GC tree does not pass the build, the PTB tree does not update!')

def pvtb_tree_run_4sanity(target, stable_tree):
    call_from_sys('mv /project/hawaii/a0/arch/archpv/'+ stable_tree + '/out ' + '/project/hawaii/a0/arch/archpv/'+ stable_tree + '/out.last.bak')
    with open('/project/hawaii/a0/arch/archpv/' + gc_sanity_tree + '/sanity_status', 'r') as f:
        gc_tree_status = f.readlines()[0]
    if gc_tree_status == '0':
        logging.info(parting_line + 'Start at:  ' + get_now('all', True) + parting_line)
        os.chdir('/project/hawaii/a0/arch/archpv/' + stable_tree + '/') # change the directory and print the time
        logging.info(os.getcwd())
        logging.info(' ##########  This is PVTB Tree Compile  ##########')
        pvtb_tree_run_compile()
        judge_whether_have_file(target, stable_tree)
        logging.info(' ##########  This is PVTB Tree Simulation ##########')
        with open(target + stable_tree + '/compile_sanity_status') as cf:
            compile_status = cf.readlines()[0]
        compile_status = '0'
        if compile_status == '0':
            lock = Lock()
            processes = []
            for one_sanity_test in cmd_4sanity:
                cmd = 'apy /project/hawaii/a0/arch/archpv/tree1forcp_pvtb_sanity_tree/pvtb/script/run_ptb.py -flow s --dump_fsdb --backdoor_sh_mem_enable -tc 500000 -t ' + one_sanity_test
                p = Process(target = pvtb_tree_run_sim_lock, args = (cmd, lock))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
            sim_pass_num_sum = 0
            for test_name in cmd_4sanity:
                one_test_sim_flag = judge_whether_have_str(target, stable_tree, test_name)
                sim_pass_num_sum += one_test_sim_flag
            open(target + stable_tree + '/simulation_sanity_status', 'w').write(str(sim_pass_num_sum))
            with open(target + stable_tree + '/simulation_sanity_status') as sf:
                simulation_status = sf.readlines()[0]
            if simulation_status == '0':
                open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/whether_run_flag', 'w').write('had_run')
                if stable_tree == 'tree1forcp_pvtb_sanity_tree':
                    open('/project/hawaii/a0/arch/archpv/tree2forcp_pvtb_sanity_tree/whether_run_flag', 'w').write('have_not_run')
                else:
                    open('/project/hawaii/a0/arch/archpv/tree1forcp_pvtb_sanity_tree/whether_run_flag', 'w').write('have_not_run')
        else:
            logging.info('      PVTB Compile Fail, No Simulation ')
            open(target + stable_tree + '/simulation_sanity_status', 'w').write('1')
        logging.info(' ##########  End  ##########')
        logging.info(blank_line)
    else:
        logging.info('Since the GC tree does not pass the build, the PVTB tree does not update!')
    call_from_sys('mv /project/hawaii/a0/arch/archpv/'+ gc_sanity_tree + '/out ' + '/project/hawaii/a0/arch/archpv/'+ gc_sanity_tree + '/out.last.bak')

def pvtb_git_pull(stable_tree, target, key):
    pvtb_target = target + 'tree2forcp_pvtb_sanity_tree/pvtb'
    git_cmd = 'git pull'
    try:
        child = pexpect.spawn(git_cmd, cwd = pvtb_target)
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
                    #print('GitPull Successed!')
                    logging.info('GitPull Successed!')
                elif 'fatal:' in output or 'error:' in output:
                    #print('GitPull Failed')
                    logging.info('GitPull Failed')
            else:
                logging.info('GitPull Timeout')
        elif index == 1:
            logging.info('GitPull Successed!')
        elif index == 2:
            logging.info('GitPull Timeout')
    except :
        logging.info('GitPull Failed!')

def pvtb_copy_and_git(stable_tree, target, key):
    os.chdir('/project/hawaii/a0/arch/archpv/' + stable_tree + '/') # change the directory and print the time
    call_from_sys('mv pvtb pvtb.bk')
    call_from_sys('mv out out.bk')
    call_from_sys('csh -c "source ~/.cshrc"')
    with open('/project/hawaii/a0/arch/archpv/' + gc_sanity_tree + '/sanity_status', 'r') as f:
        ngtb_status = f.readlines()[0]
    if ngtb_status.strip() == '0':
        logging.info(' ##########  This is copy ... ##########')
        if stable_tree == 'tree1forcp_pvtb_sanity_tree':
            new_pvtb_copy_cmd = pvtb_copy_cmd_tree1%(stable_tree)
            copy_changelist(stable_tree, target)
        else:
            new_pvtb_copy_cmd = pvtb_copy_cmd_tree2%(stable_tree)
            copy_changelist(stable_tree, target)
        copy_info = call_from_sys(new_pvtb_copy_cmd)   
        logging.info(copy_info)
        logging.info(' ##########  Copy done ... ##########')
        #logging.info(' ##########  This is GitPull ... ##########')
        #pvtb_git_pull(stable_tree, target, key)
    else:
        pass

def copy_changelist(stable_tree, target):
    configuration_id_dir = '/project/hawaii/a0/arch/archpv/ptb_sanity_tree/configuration_id'
    call_from_sys('cp ' + configuration_id_dir + ' ' + target + stable_tree + '/configuration_id')

def cmd_crontab(stable_tree, target, key):
    ngtb_tree_run(gc_sanity_tree)
    ngtb_files_change(target, gc_sanity_tree)
    pvtb_copy_and_git(stable_tree, target, key)
    #pvtb_tree_run(target, stable_tree)
    pvtb_tree_run_4sanity(target, stable_tree)

if __name__=='__main__':
    opt = option_parser()
    target = '/project/hawaii/a0/arch/archpv/'
    cmd_crontab(opt.tree, target, opt.key)


