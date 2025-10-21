#!/usr/bin/env /tools/ctools/rh7.9/anaconda3/2023.03/bin/python3
# -*- coding: utf-8 -*-
"""
@Describe: Run ptb compile, Generate ptb test, Run ptb simulation
@Author: Guo Shihao
Data: 2025.07.01
"""

import os, re, sys, time, stat, pdb, shutil, argparse, pexpect, time, logging, multiprocessing
from pathlib import Path
from functools import partial
from optparse import OptionParser
import random

#cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
#STEM = cdir + '../../'
try:
    STEM = os.getenv('STEM')
    STEM = STEM if STEM.endswith('/') else STEM + '/'
    os.chdir(STEM)
except:
    print('Please \'source env_dir.sh\' before use this script')
    sys.exit()
os.makedirs('logs', exist_ok = True)
logger = multiprocessing.get_logger()
logging.basicConfig(filename='logs/ptb_execute_info.log', level=logging.INFO)
#formatter = logging.Formatter('[%(asctime)s]', datefmt = '%Y-%m-%d %H:%M:%S')
#console_handler = logging.StreamHandler()
#console_handler.setFormatter(formatter)
#logger.addHandler(console_handler)

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()

    def flush(self):
        for f in self.files:
            if hasattr(f, 'flush'):
                f.flush()

class RunPTB():

    def __init__(self,xcdmode='cache_sanity_test',fgp_num='0'):
        self.xcdmode=xcdmode
        self.dir_name = f'{xcdmode}'
        self.fgp_num=fgp_num
        if (self.fgp_num!=0):
            self.dir_name = f'{xcdmode}_fgp'
        self.compile_cmd_base = f'bsub -Is vcs +error+1 -sverilog -ntb_opts uvm-1.2 -lca -full64 -debug_access+r -MMD -MV -kdb -assert novpi+dbsopt -Xkeyopt=amd1 -reportstats -top tb -l $STEM/out/compile/{self.dir_name}/vcs.com_log -Mupdate -ld /tool/hydora64/hdk-r7-9.2.0/22.10/bin/g++ +vcs+lic+wait -override_timescale=1ps/1ps -assert svaext +define+COSIM_LIB_UNAVAILABLE -psl +vpi +nospecify +notimingchecks +lint=CDOB +lint=PCWM +lint=ERASM +lint=TFIPC -error=DPIMI +warn=all -L$STEM/src/tmpcomp  -LDFLAGS -L$STEM/pvtb/src/lib_socpmdl -lTcEa_adpator -LDFLAGS "-Wl,-rpath,$STEM/src/tmpcomp" -P $STEM/src/tmpcomp/msgio.tab -lmsgio_pli -P $STEM/src/tmpcomp/vecio.tab -lvecio_pli -P $STEM/src/tmpcomp/ati_random.tab -lati_random_pli -lsh_bfm_common_dpi -ldummy_sc_main -lm -full64 -LDFLAGS "-ggdb" +define+DISABLE_SQC_CACHE_CHECKER +define+PA_FCOV_ON +define+MC_IP_ABV_FUNC_EN=0 -Xnjoshi=0x10000 -debug_region=cell+lib +warn=IEELMME +define+PVTB_BWC +define+PVTB_CP_SHELL +define+CPC_DC0_RTL +define+PVTB_BWC_1DIE +define+PVTB_EA_RTL_OMIT +define+SOC_MODEL -f $STEM/pvtb/ptb_cmd/'
        if self.xcdmode in ('1xcd','cache_sanity_test'):
            self.compile_cmd = f'{self.compile_cmd_base}from_timescale.compfiles.bwc.xf'
        elif self.xcdmode=='2xcd':
            self.compile_cmd = f'{self.compile_cmd_base}from_timescale.compfiles_2xcd.bwc.xf +define+PVTB_2DIE_RTL'
        elif self.xcdmode=='4xcd':
            self.compile_cmd = f'{self.compile_cmd_base}from_timescale.compfiles_4xcd.bwc.xf +define+PVTB_4DIE_RTL'
        elif self.xcdmode in ('4xcd_mix'):
            self.compile_cmd = f'bsub -Is vcs +error+1 -sverilog -ntb_opts uvm-1.2 -lca -full64 -debug_access+r -MMD -MV -kdb -assert novpi+dbsopt -Xkeyopt=amd1 -reportstats -top tb -l $STEM/out/compile/{self.dir_name}/vcs.com_log -Mupdate -ld /tool/hydora64/hdk-r7-9.2.0/22.10/bin/g++ +vcs+lic+wait -override_timescale=1ps/1ps -assert svaext +define+COSIM_LIB_UNAVAILABLE -psl +vpi +nospecify +notimingchecks +lint=CDOB +lint=PCWM +lint=ERASM +lint=TFIPC -error=DPIMI +warn=all -L$STEM/src/tmpcomp  -LDFLAGS -L$STEM/pvtb/src/lib_socpmdl -lCoreModel -LDFLAGS "-Wl,-rpath,$STEM/src/tmpcomp" -P $STEM/src/tmpcomp/msgio.tab -lmsgio_pli -P $STEM/src/tmpcomp/vecio.tab -lvecio_pli -P $STEM/src/tmpcomp/ati_random.tab -lati_random_pli -lsh_bfm_common_dpi -ldummy_sc_main -lm -full64 -LDFLAGS "-ggdb" +define+DISABLE_SQC_CACHE_CHECKER +define+PA_FCOV_ON +define+MC_IP_ABV_FUNC_EN=0 -Xnjoshi=0x10000 -debug_region=cell+lib +warn=IEELMME +define+PVTB_BWC +define+PVTB_CP_SHELL +define+CPC_DC0_RTL +define+PVTB_BWC_1DIE +define+PVTB_EA_RTL_OMIT -f $STEM/pvtb/ptb_cmd/from_timescale.compfiles.bwc.xf +define+SHAOBO_1RTL_3MODEL_ENV'#delete -lTcEa_adpator add -lCoreModel
        if (self.fgp_num!=0):
            self.compile_cmd = f'{self.compile_cmd} -fgp'
        random_number = random.randint(10_000_000,99_999_999)
        self.sim_cmd_base = f'bsub -W 480:00 -Ip -q regr_high $STEM/out/compile/{self.dir_name}/simv -l ./vcs_run.log +vcs+lic+wait -assert verbose+errmsg -assert nopostproc +seed={random_number} +ntb_random_seed={random_number} -reportstats +uvm_tr_disable -assert global_finish_maxfail=1000000  +UVM_TESTNAME=cache_sanity_test +testname=%s +UVM_TIMEOUT=2000000000 +UVM_VERBOSITY=UVM_MEDIUM +UVM_OBJECTION_TRACE +UVM_PHASE_TRACE %s'

        self.total_args = ''
        self.path_args = ' -l ' + STEM + '/pvtb/src/test/isa'
    
    def hex_type(self, value):
        try:
            if value.lower().startswith(('0x', '0X')):
                return hex(int(value, 16))
            return hex(int(value, 16))
        except ValueError:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid hexadecimal number. Please use a format like '1A' or '0x1A'")


    def run_cmd_func(self):
        
        pass

    def rm_one_file(self, target):
        try:
            os.remove(target)
        except:
            pass
    
    def copy_one_path(self, src_dir, tar_dir):
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
                except:
                    pass

    def compile_child_run(self, target):
        with open('logs/ptb_compile.log', 'wb') as logfile:
            child = pexpect.spawn('/tool/pandora/bin/tcsh')
            #child.logfile = logfile
            tee = Tee(logfile, sys.stdout.buffer)
            child.logfile = tee
            try:
                start_time = time.time()
                print('Currently Executing Compile')
                child.sendline("source " + target + "/pvtb/env_dir.sh")
                child.expect(r'\n', timeout = 10)
                child.sendline('echo $STEM')
                child.expect(r'\n', timeout = 5)
                child.sendline(f'cd out/compile/{self.dir_name}/')
                child.expect(r'\n', timeout = 5)
                child.sendline('rm -rf simv')
                child.expect(r'\n', timeout = 5)
                #child.sendline('bsub -W 0:30 -Is ../../../pvtb/vcs_compile_psm.run_bwc')
                child.sendline(self.compile_cmd)
                match_index = child.expect([r'CPU time', pexpect.EOF, pexpect.TIMEOUT], timeout = 18000) # 1800 = 30 minutes
                elapsed_time = time.time() - start_time
                logging.info('      PTB Compile Total Used Time: ' + str(elapsed_time))
                if match_index == 0:
                    logging.info('      PTB Compile End')
                    print('PTB Compile End')
                elif match_index == 1:
                    logging.info('      PTB Compile TimeOut ~_~')
                    print('PTB Compile Fail')
            except Exception as e:
                print(f'Error: {str(e)}')
            finally:
                if child.isalive():
                    child.close()
        
    def gen_test_exec(self, target, testname):
        testname_only = testname.split(' ')[0]
        with open(f'logs/ptb_generate_test_{testname_only}.log', 'wb') as logfile:
            child = pexpect.spawn('/tool/pandora/bin/tcsh')
            #child.logfile = logfile
            tee = Tee(logfile, sys.stdout.buffer)
            child.logfile = tee            
            execute_command = '/tools/ctools/rh7.9/anaconda3/2023.03/bin/python3 $STEM/pvtb/src/gkt/shells/select_and_run_gen.py ' + testname + self.test_args# + self.path_args
            try:
                start_time = time.time()
                print('Currently Executing Generate Test')
                child.sendline("cd " + target)
                child.expect(r'\n', timeout = 10)
                child.sendline("source " + target + "/pvtb/env_dir.sh")
                child.expect(r'\n', timeout = 10)
                child.sendline('echo $STEM')
                child.expect(r'\n', timeout = 10)
                child.sendline('cd $STEM/pvtb/src/gkt/shells')
                child.expect(r'\n', timeout = 10)
                child.sendline(execute_command)
                match_index = child.expect([r'End', pexpect.EOF, pexpect.TIMEOUT], timeout = 1200)
                elapsed_time = time.time() - start_time
                logging.info('      PTB Generate Test Total Used Time: ' + str(elapsed_time))
                if match_index == 0:
                    print('PTB Generate Test End')
                    logging.info('      PTB Generate Test End')
                elif match_index == 1:
                    logging.info('      PTB Generate Test TimeOut ~_~')
                    print('PTB Generate Test Fail')
            except Exception as e:
                print(f'Error: {str(e)}')
            finally:
                if child.isalive():
                    child.close()
        self.copy_one_path(STEM + '/pvtb/src/gkt/gkt_out/' + testname_only, STEM + '/pvtb/src/test/isa/' + testname_only)
        
    def simulation_child_run(self, target, total_args, test_last_dir, testname):
        logger = multiprocessing.get_logger()
        with open(STEM + '/logs/ptb_simulation_' + testname + '.log', 'wb') as logfile:
            child = pexpect.spawn('/tool/pandora/bin/tcsh')
            #child.logfile = logfile
            tee = Tee(logfile, sys.stdout.buffer)
            child.logfile = tee          
            cmd = self.sim_cmd_base%(test_last_dir + '/' + testname, total_args)
            print(cmd)
            try:
                start_time = time.time()
                print('Currently Executing Simulation')
                child.sendline("source " + STEM + "/pvtb/env_dir.sh")
                child.expect(r'\n', timeout = 10)
                child.sendline('cd $STEM')
                child.expect(r'\n', timeout = 5)
                child.sendline('mkdir -p out/run/' + testname)
                child.expect(r'\n', timeout = 5)
                child.sendline('cd out/run/' + testname)
                child.expect(r'\n', timeout = 5)
                child.sendline(self.sim_cmd_base%(test_last_dir + '/' + testname, total_args))
                match_index = child.expect([r'CPU Time', pexpect.EOF, pexpect.TIMEOUT], timeout = 1728000) # 24 hours*20
                elapsed_time = time.time() - start_time
                logger.info('      PTB Simulation Total Used Time: ' + str(elapsed_time))
                logging.info('      PTB Simulation Total Used Time: ' + str(elapsed_time))
                if match_index == 0:
                    logging.info('      PTB Simulation End')
                    print('PTB Simulation End')
                elif match_index == 1:
                    logging.info('      PTB Simulation TimeOut ~_~')
                    print('PTB Simulation TimeOut')
            except Exception as e:
                print(r'Error: {str(e)}')
            finally:
                if child.isalive():
                    child.close()

    def run_simulaiton_all_exe(self, target, total_args):
        try:
            os.chdir(target)
            current_dir = Path.cwd()
            folders = [item.name for item in current_dir.iterdir() if item.is_dir()]
            print(folders)
        except:
            print(current_dir + ' not exist')
        simulation_with_fixed_target_isa = partial(self.simulation_child_run, target, 'isa', total_args)
        simulation_with_fixed_target_opr = partial(self.simulation_child_run, target, 'opr', total_args)
        simulation_with_fixed_target_sanity = partial(self.simulation_child_run, target, 'sanity', total_args)
        with multiprocessing.Pool(processes = 40) as pool:
            results = pool.map(simulation_with_fixed_target_isa, folders)
            #results = pool.map(simulation_with_fixed_target_opr, folders)
            #results = pool.map(simulation_with_fixed_target_sanity, folders)

    def walk_with_depth(self, target, testname_only, max_depth):
        start_depth = target.count(os.sep)
        last_dir = ''
        for root, dirs, files in os.walk(target):
            current_depth = root.count(os.sep) - start_depth
            if current_depth >= max_depth:
                dirs[:] = []
                continue
            if testname_only in dirs:
                last_dir = root.split('/')[-1]
                break
        return last_dir

    def test_last_directory(self, target, testname_only, max_depth):
        dir_list = ['sanity', 'isa', 'opr']
        test_last_dir = ''
        for dir in dir_list:
            target_ = target + dir
            test_last_dir = self.walk_with_depth(target_, testname_only, max_depth)
            print(f'DEBUG test_last_dir:{test_last_dir}')
            if test_last_dir:
                break
        if test_last_dir == '':
            print('Error: cannot find your test in the isa, opr or sanity paths')
            sys.exit()
        return test_last_dir

    def compile_exec(self, target):
        comp_dir = (target + f'out/compile/{self.dir_name}/')
        os.makedirs(comp_dir, exist_ok = True)
        os.chdir(target)
        self.compile_child_run(target)

    def simulation_exec(self, flow, target, testname, total_args):
        #if 'g' in flow:
        target = target + 'pvtb/src/test/'
        if testname:
            testname_only = testname.split(' ')[0]
            test_last_dir = self.test_last_directory(target, testname_only, 1)
            print('Test ' + testname_only + ' Simulation Start')
            self.simulation_child_run(target, total_args, test_last_dir, testname_only)
            print('Test ' + testname_only + ' Simulation End')
        else:
            self.run_simulaiton_all_exe(target, total_args)
        #else:
        #    #total_args += self.exist_args
        #    if testname:
        #        testname_only = testname.split(' ')[0]
        #        print('Test ' + testname_only + ' Simulation Start')
        #        self.simulation_child_run(target, total_args, testname)
        #        print('Test ' + testname_only + ' Simulation End')
        #    else:
        #        target = target + '/pvtb/src/test/isa'
        #        self.run_simulaiton_all_exe(target, total_args)

    def fun_exec(self, flow, target, testname, total_args):
        if 'c' in flow:
            self.compile_exec(target)
        if 'g' in flow:
            if testname == None:
                print('Please input your testname for generate GKT test.')
            else:
                self.gen_test_exec(target, testname)
        if 's' in flow:
            self.simulation_exec(flow, target, testname, total_args)

    def option_parser(self, *args):
        arg_descript = '''
        c: compile
        g: gen_test
        s: simulation        '''
        parser = argparse.ArgumentParser(description='Run specified function%s'%arg_descript, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-flow', '--flow', default = None, dest = 'flow', help= 'e.g. [cgs|cg|cs|gs|c|g|s]')
        parser.add_argument('-t', '--testname', default = None, dest = 'testname', help= 'Run the test you specified')
        parser.add_argument('-pn', '--pipe_num', type = int, default = 1, dest = 'pipe_num', help= 'The dispatch correspoding to pipe1 placed in the pipe1 subdirectory under the use case directory')
        parser.add_argument('-dn', '--dispatch_num', type = int, default = 1, dest = 'dispatch_num', help= 'The second dispatch placed in the subdirectory named 0 under the case directory')
        parser.add_argument('-qn', '--queue_num', type = int, default = 1, dest = 'queue_num', help= 'Specify the number of queues running sequentially in a single pipe within the CP')
        parser.add_argument('-tc', '--timeout_wait_cycles', type = int, default = 5000, dest = 'timeout_wait_cycles', help= 'Set the timeout period for the watchdog in the environment')
        parser.add_argument('-ds', '--dump_addr_size', type = self.hex_type, default = None, nargs = 2, dest = 'dump_addr_size', help= r'These three options are used in combination: +dump_enable +dump_addr=%%h +dump_dump_size=%%h')
        #parser.add_argument('-e', '--execute_command', default = None, dest = 'execute_command', help= 'The execute command you used, which is used for generating GKT test')
        #parser.add_argument('--use_gen', action = 'store_true', help= 'Using the generated test' )
        parser.add_argument('-be', '--backdoor_sh_mem_enable', action = 'store_true', help= 'Initialize LDS, VGPR and SGPR' )
        parser.add_argument('-we', '--warmup_enable', action = 'store_true', help= 'Warmup Enable' )
        parser.add_argument('-rpl', '--gen_rpl', action = 'store_true', help= 'Gen Rpl' )
        parser.add_argument('-unodr', '--unordered', action = 'store_true', help= 'Unordered Enable' )
        parser.add_argument('-le', '--l2cache_flush_enable', action = 'store_true', help= 'L2 cache flush enable ' )
        parser.add_argument('-df', '--dump_fsdb', action = 'store_true', help= 'Dump waveform for your tests' )
        parser.add_argument('-mo', '--monitors_off', action = 'store_true', help= 'Turn off all the monitors' )
        parser.add_argument('-only_opr_monitor', '--only_opr_monitor', action = 'store_true', help= 'Turn on the sq_spi_msg_monitor' )
        parser.add_argument('-pe', '--perfcount_enable', action = 'store_true', help= 'Turn on perfcount_enable' )
        parser.add_argument('-coen','--coissue_enable', action = 'store_true', help= 'Coissue Enable' )
        parser.add_argument('-page','--pagetable_enable', action = 'store_true', help= 'Pagetable' )
        parser.add_argument('-wdd','--watchdog_disable', action = 'store_true', help= 'Watchdog Disable' )
        parser.add_argument('-um', '--use_new_unoder_mode', action = 'store_true', help= 'Use new under mode' )
        ##if 'regression' in args:
        parser.add_argument('-d', '--desc', default= 'shaobo_ip', dest= 'desc', help = 'Project for [shaobo_ip | shaobo_ip]')
        parser.add_argument('-a', '--algo', default= 'spisq_launch', dest= 'algo', help = 'Measure method used to calculate the rate,  the format must be \'["str",...]\'')
        parser.add_argument('-r', '--regr', default= 'shader', dest= 'regr', help = 'Regression type on different projects. [shader|cache|command|sanity|rerun]')
        parser.add_argument('-m', '--mode', default= None, dest= 'mode', help = 'Regression mode of how tests are dispatched. [postproc]')
        parser.add_argument('--exe', default = False, action='store_true', dest= 'exe', help= 'Execute the regression, by default it only print commands')
        parser.add_argument('-xcdmode','--xcdmode', choices=['1xcd','2xcd','4xcd','4xcd_mix','cache_sanity_test'],default='cache_sanity_test',help='Compilation mode')#zy_add_0923
        parser.add_argument('-fgp_num', '--fgp_num', type = int, default = 0, dest = 'fgp_num' , help= 'Use fgp' )#zy_add_0926
        options = parser.parse_args()  
        return options

    def get_total_args(self):
        opt = self.option_parser()
        total_args = self.total_args
        #self.test_args = ' -c shaobo --debug --output --base 0x10000000 '
        self.test_args = ' -c shaobo --debug --base 0x10000000 '
        if opt.xcdmode:
            total_args += f'+xcdmode={opt.xcdmode} '
            print(f'xcdmode: {opt.xcdmode}')
        if opt.xcdmode=='4xcd_mix':
            total_args += '+pagetable_enable=1'
            print('DEBUG +pagetable_enable=1')
        if opt.pipe_num:
            total_args += f'+pipe_num={opt.pipe_num} '
        if opt.dispatch_num:
            total_args += f'+dispatch_num={opt.dispatch_num} '
        if opt.queue_num:
            total_args += f'+queue_num={opt.queue_num} '
        if opt.timeout_wait_cycles:
            total_args += f'+timeout_wait_cycles={opt.timeout_wait_cycles} '
        if opt.dump_addr_size:
            addr, size = opt.dump_addr_size
            total_args += f'+dump_enable +dump_addr={addr} +dump_dump_size={size} '
        if opt.backdoor_sh_mem_enable:
            total_args += '+backdoor_sh_mem=on '
        if opt.warmup_enable:
            self.test_args +=  ' -t warmup 1'
            total_args +=  ' +warmup_enable '
        if opt.unordered:
            self.test_args +=  ' +unordered'
        if (opt.gen_rpl==0):
            self.test_args +=  ' --output'#default add --output if no set --gen_rpl
        if opt.l2cache_flush_enable:
            total_args += '+l2cache_flush_enable '
        if opt.dump_fsdb:
            if opt.xcdmode=='2xcd':
                total_args += '-ucli -do $STEM/pvtb/fsdb_dump_ctrl_2xcd.tcl '
                print('DEBUG opt.dump_fsdb:fsdb_dump_ctrl_2xcd.tcl')
            else:
                total_args += '-ucli -do $STEM/pvtb/fsdb_dump_ctrl.tcl '
                print('DEBUG opt.dump_fsdb:fsdb_dump_ctrl.tcl')
        if opt.fgp_num:
            if opt.dump_fsdb:
                total_args += f'-fgp=single_socket_mode -fgp=allow_less_cores -fgp=schedpli -fgp=num_fsdb_threads:1 -fgp=fsdb_adjust_cores -fgp=num_cores:{opt.fgp_num+1} '
                print(f'DEBUG dump_fsdb_enable:fgp_num:{opt.fgp_num+1}')
            else:
                total_args += f'-fgp=single_socket_mode -fgp=allow_less_cores -fgp=schedpli -fgp=num_cores:{opt.fgp_num} '
                print(f'DEBUG dump_fsdb_off:fgp_num:{opt.fgp_num}')
        if not (opt.monitors_off|opt.only_opr_monitor):
            total_args += '+all_monitors=on '
        elif opt.only_opr_monitor:
            total_args += '+sq_spi_msg_monitor=on +tcp_dbg_off +cgt_assert_disable'#add sq_spi_msg_monitor only 
        if opt.perfcount_enable:
            total_args += '+perfcount_enable '
        if opt.coissue_enable:
            total_args +=  '+coissue_enable'
        if opt.watchdog_disable:
            total_args += '+watchdog_disable'
        if opt.pagetable_enable:
            total_args +=  '+pagetable_enable'
        if opt.use_new_unoder_mode:
            total_args += '+use_new_unoder_mode '

        else:
            pass
        return total_args

    def update_mode(self,new_xcdmode ,new_fgp_num):
        if new_xcdmode !=self.xcdmode:
            self.xcdmode=new_xcdmode
        if  new_fgp_num!=self.fgp_num:
            self.fgp_num=new_fgp_num
        self.__init__(xcdmode=self.xcdmode,fgp_num=self.fgp_num)

if __name__ == '__main__':
    rp = RunPTB()
    opt = rp.option_parser()
    total_args = rp.get_total_args()
    rp.update_mode(opt.xcdmode,  opt.fgp_num)
    rp.fun_exec(opt.flow, STEM, opt.testname, total_args)

