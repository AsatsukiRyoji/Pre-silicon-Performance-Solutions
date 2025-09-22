#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression system

@author:  Li Lizhao
"""
import os,sys,re, pdb
from pandas import DataFrame as DF
#import multiprocessing as mp
##wrapper of threading but has the same API of multiprocessing
import pandas as pd
import multiprocessing.dummy as md
import threading
from functools import partial

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir+'../')
from utility import util
import check.core_performance_check as cpc
import check.test_performance_check as tpc
##Shihao TODO: how to let message from subprocess printed in running terminal
stem = os.environ.get('STEM')+'/' if os.environ.get('STEM') else cdir + '../'
#stem = cdir + '../../../../../../../'

from testpm.perf_buffer_store_pm import BufferStorePM 
from testpm.perf_buffer_load_pm import BufferLoadPM 
from testpm.perf_buffer_load_to_lds_pm import BufferLoadtoLdsPM 
from testpm.perf_global_store_pm import GlobalStorePM 
from testpm.perf_global_load_pm import GlobalLoadPM 
from testpm.perf_global_load_to_lds_pm import GlobalLoadtoLdsPM
from testpm.perf_flat_store_pm import FlatStorePM 
from testpm.perf_flat_load_pm import FlatLoadPM 
from testpm.perf_flat_load_to_lds_pm import FlatLoadtoLdsPM
from testpm.perf_matrix_copy_to_lds_pm import MatrixCopytoLdsPM 
from testpm.perf_matrix_copy_pm import MatrixCopyPM 

class RegrSystem:
    
    def __init__(self,):
        '''
        
        Returns
        -------
        None.

        '''
        self.lsf_cmd = {'bsub':'lsf_bsub -Is %s'}
        ##Shihao TODO: choose queue wisely and automatically
        self.bsub_opt = {'que': '-q regr_high ', 'job': '-J %s '}
        self.dj_cmd = {'run_test': "dj -c -e 'run_test %s'"}
        self.dj_opt = {
            ##NOTE: m:100 means 100 parallel run tasks from one DJ command, especially on multi-test
            'basic'     : '-J lsf -m80 -DGC_PERF -DSKIP_CAT_EMU_VEC ',
            'dvonly'    : '-DRUN_DV=ONLY ',
            'dvoff'     : '-DRUN_DV=OFF ',
            'bldtest'   : '-j build_test ',
            'log'       : "-l "+stem+'logs/'+"%s.log ",
            'dv_dbg_log': '--save_cmd_logs ',
            'hash_en'   : '-DTC_HASH_ENABLE ',
            'dump_wave' : '-DFSDB_RUNTIME_CTRL -DDUMP_WAVE_WITH_LIBFILE -DDUMP_ITRACE '}
        self.dv_cmd = {'test': '"%s"'}
        self.dv_opt = {'emu_only': '-fte'}
        self.lists = {
                'kongming_ip': 'perf_kongming_ip.testlist'
                ,'bowen_ip': 'perf_bowen_ip.testlist'
                ,'bowen_b0_ip': 'perf_bowen_b0_ip.testlist'
                ,'run_again': 'perf_run_again.testlist'
        }
        self.meth_desc = util.get_cfg_f(cdir+'../methodology.cfg')
        regr_col_l = self.meth_desc['regression_col'].split(',')
        self.result_df = DF(columns=regr_col_l)
        #self.regr_result_temp_f = cdir+'regr_result_temp.csv'
        ##Use 'with open' to create the file or reset it with 'w'
        #with open(self.regr_result_temp_f, 'w') as f:
        #    f.write("REGRESSION TEMPORARY RESULT")
        
        self.lock = threading.Lock()
        self.log = util.PMLog(name='perf_regression_%s' %util.get_now(), path=cdir)
        self.hbo_cmd = "dj -c -v -e 'here_in_design.build_self()'"
        self.hbo_dir = ['command', 'shader', 'cache']
    
    def get_tests(self, desc, rgr_type):
        '''
        Parameters
        ----------
        desc : str
            description file name
        rgr_type : str
            regression type

        Returns
        -------
        testlist : dict {str:list,}
            test list 

        '''
        rgr_d = util.get_cfg_f(cdir+self.lists[desc], True, sec=rgr_type.upper())
        testlist = {}
        for k,v in rgr_d.items():
            #testlist[k] = [list(set(util.get_test_desc(dv, v, []))), v]
            ptn = '(\w+)(-sub\d+)?'
            _grp = re.search(r''+ ptn +'', k).groups()
            _g, _s = _grp[0], _grp[1]
            dv = cdir+'../../'+self.meth_desc[_g+'_home']+_g+'.dv'
            tests_ = list(set(util.get_test_desc(dv, v, [])))
            if _s != None and testlist.get(_g) != None:
                testlist[_g][0].extend(tests_)    
                testlist[_g][1].extend([v])
            else:
                testlist[_g] = [tests_]
                testlist[_g].append([v])
            #NOTE|OD.keys() is set-like, use 'set' can transfer it to 'set' type easily
            ##NOTE|This is an examing mechanism to assure required tests from regression testlist 
        return testlist
    
    def run_regr(self, desc, rgr_type, mode='postproc',  no_build=False, exe=False, dump=False, hash_en=False, gui_en=False, **kw):
        ##[XXX]Fool-proofing of regression triggering
        #if util.protector() == 'PASS': pass
        #else: sys.exit()
        #Change to stem to execute
        os.chdir(stem)
        runcmd = self.lsf_cmd['bsub']
        runopt = self.bsub_opt['que'] 
        jobname = desc+'_perf_regr_job_start_at_'+util.get_now('dhms')
        runopt += self.bsub_opt['job'] %jobname
        runcmd = runcmd %runopt
        
        dvcmd = self.dv_cmd['test'] 
        djcmd = self.dj_cmd['run_test']
        djcmd = djcmd %dvcmd
        djopt = self.dj_opt['basic']
        if os.path.isdir(stem+'logs') == False:
            os.makedirs(stem+'logs')
        djopt += self.dj_opt['log']
        djcmd += ' ' + djopt
        runcmd += djcmd        
        if no_build == False and mode != 'postproc':
            #_, build_tests = (self.get_tests(desc, 'build')).popitem()
            for k,build_tests in self.get_tests(desc, 'build').items():
            #'dvoff' is once for building
                build_cmd = (runcmd %('perf/'+build_tests[0][0],'TREEBUILD@'+build_tests[0][0])) + self.dj_opt['dvoff']
                self.log.info('[BUILD BEGIN]%s' %(build_cmd))
            #If there are more tests in build_testlist that would be an ignorable issue
            #DBG|build_cmd = 'date'
            if exe :
                result, status = util.call_from_sys(build_cmd, has_status=True)
                if status == 0:
                    #pdb.set_trace()
                    self.log.info('[BUILD PASSED]Test: %s' %(build_tests[0]))
                    #run command to hbo under shader/ command/ and cache/
                    for item_dir in self.hbo_dir:
                        try:
                            os.chdir(stem + 'src/test/suites/block/perf/' + item_dir + '/')
                            util.call_from_sys(self.hbo_cmd)  
                        except:
                            pass
                    os.chdir(stem)
                    pass
                else:
                    self.log.error('[BUILD FALED]Test: %s, status: [%s]' %(build_tests[0], status))
                    sys.exit()
            else :
                print(build_cmd)
        run_testlist = self.get_tests(desc, rgr_type)
        #Only dv only is required after tree building
        if mode == 'multi':
            runcmd += self.dj_opt['dvonly']
        elif mode == 'single':
            runcmd += self.dj_opt['bldtest']
        elif mode == 'rerun':
            runcmd += self.dj_opt['dvonly']
        if dump == True:
            runcmd += self.dj_opt['dump_wave']
        if hash_en == True:
            runcmd += self.dj_opt['hash_en']
        sim_cmds = {}  
        total_tests = 0
        #A group in run_testlist is one item "<subgroup@>group : [test1,test2...]"
        for k,v in run_testlist.items():
            if k in ['perf_matrix_load_to_lds', 'perf_buffer_atomic', 'perf_global_atomic', 'perf_matrix_copy_to_lds'] and hash_en ==False:
                runcmd += self.dj_opt['hash_en']
            if mode == 'single':
                sim_cmds[k] = [(t, runcmd %('perf/'+t,'REGRESSION@'+t)) for t in v[0]]
            elif mode == 'multi':
                sim_cmds[k] = (v[0], runcmd %(' '.join(list(map(lambda x: 'perf/'+x, v[0]))),k))
            elif mode == 'postproc':
                sim_cmds[k] = ('POSTPROC ONLY', v[1])
            runcmd = runcmd.replace('-DTC_HASH_ENABLE ', '')
            
        if exe :
            self.async_engine(self.sim_and_postproc, desc, rgr_type, sim_cmds, mode=mode)
            if mode != 'postproc':
                #read every perf_check_result.csv' under test output to self.result_df
                try: edir = os.environ.get('PV_GC_OUT')+'/'
                except: edir = self.meth_desc['default_output_home'] %(stem)
                for d in os.listdir(edir):
                    f = d + '_perf_check_result.csv'
                    try:
                        _ = pd.read_csv(edir+d+'/'+f).drop(['Unnamed: 0'], axis = 1)
                        self.result_df = self.result_df.append(_, ignore_index = True)
                    except:
                        continue
                #pdb.set_trace()
            
            _changelist = open(stem + '/configuration_id', 'r').read()
            changelist = re.search(r'(\d+)', _changelist).groups()[0]
            self.result_df.to_csv(cdir+desc+'_'+rgr_type + '_cl_' + changelist + '_regression_result_' + util.get_now('ymd')+'.csv', float_format = '%.3f',mode = 'w')
            if gui_en:
                gui = util.PMGui()
                gui.run([self.result_df])
        else :
            for k, c in sim_cmds.items() :
                print(k, c)

    def async_engine(self, func, desc, rgr_type, sim_cmds, **kw):
        #NOTE: use 'pdb.set_trace()' can break in subprocess, '-m pdb' can not
        threads = []
        sim_pool = md.Pool(processes=len(sim_cmds))
        #with mp.Pool(processes=len(sim_cmds)) as simp:
        for k,v in sim_cmds.items():
            threads.append(sim_pool.apply_async(func=func, args=(desc,k,v[1]),kwds=kw,))
        sim_pool.close()
        thd_pool = md.Pool(processes=len(threads))
        for t in threads:
            #dispatching 'get' of every thread as a timeout mechanism. 864000 = 10 days
            thd_pool.apply_async(t.get(864000))
        thd_pool.close()
        thd_pool.join()
        sim_pool.join()

    def sim_and_postproc(self, desc, group, cmd, **kw):
        #DBG|cmd = "date" 
        if kw.get('mode') == 'postproc':
            self.log.info("[POSTPROC ONLY BEGIN]")
            r, s = 'POSTPROC ONLY', 0
            for c in cmd:
                self.test_postproc(desc, group, c)
        else:
            #pdb.set_trace()
            self.log.info("[SIM BEGIN]%s" %(cmd))
            r, s = util.call_from_sys(cmd, has_status=True)
        if s == 0: #simulation end normally
            #TODO|Analyze VCS run log and dj log to distinguish TEST itself pass or not
            self.log.info("[SIM PASSED]%s. [result]%s [status]%d" %(cmd, r, s))
        else:
            self.log.error("[SIM FAILED]%s [result]%s [status]%d" %(cmd, r, s))
        return cmd #For debug. postproc's cmd is not the real one

    def test_postproc(self, desc, group, tests):
        '''Group test postprocessing
        :test_l: list. tests belong to the same testgroup getting from paramter 'group'
        '''
        ##OUT_CCPERF is set in _env/local/setup.proj to assure it exists after bootenv
        try: edir = os.environ.get('PV_GC_OUT')+'/'
        except: edir = self.meth_desc['default_output_home'] %(stem)
        self.log.info('[CHECK BEGIN]%s. Tests are [%s]' %(group, str(tests)))
        self.lock.acquire() #Keep the results in same group are stored continuously
        try:
            if 'matrix_copy' in group:
                group = group.replace('copy', 'load')
            tpm = eval(tpc.testpm_map.get(group))()
            tpm.check(desc, edir, tests)
            ##check of tpm has no return value
            self.result_df = self.result_df.append(tpm.chk_df, ignore_index=True)
            self.log.info('[%s CHECK END]' %(group))
        except: 
            self.log.error("[%s CHECK FAILED]No valid perfmodel" %group)
        self.lock.release()
        pass
        #return self.result_df
    def run_gkt_regress(self, desc, regr_type, gkt, exe=False):
        gkt_regress_dir = (stem + 'src/verif/performance/core/cache/gkt/regression/')
        os.chdir(gkt_regress_dir)
        run_testlist = self.get_tests(desc, regr_type)
        for key, tests in run_testlist.items():
            for i in range(len(tests)):
                #run_testlist[key][0][i] = tests[0][i].replace('perf', 'gkt')
                gkt_regress_cmd_g = 'python3 ' + gkt_regress_dir + 'gkt_regress.py -t ' + run_testlist[key][0][i] + ' --golden'
                gkt_regress_cmd_r = 'python3 ' + gkt_regress_dir + 'gkt_regress.py -t ' + run_testlist[key][0][i] + ' --run'
                gkt_regress_cmd_c = 'python3 ' + gkt_regress_dir + 'gkt_regress.py -t ' + run_testlist[key][0][i] + ' --compare'
                print('python3 gkt_regress.py -t ' + run_testlist[key][0][i] + ' --golden')
                print('python3 gkt_regress.py -t ' + run_testlist[key][0][i] + ' --run')
                print('python3 gkt_regress.py -t ' + run_testlist[key][0][i] + ' --compare')
                if exe == True:
                    util.call_from_sys(gkt_regress_cmd_g)  
                    util.call_from_sys(gkt_regress_cmd_r)  
                    util.call_from_sys(gkt_regress_cmd_c)  
        print('gkt testlist: %s' %run_testlist)
    
if __name__ == "__main__":
    opt = util.option_parser('regression')
    rs = RegrSystem()
    if opt.gkt == True:
        rs.run_gkt_regress(opt.desc, opt.regr, opt.gkt, opt.exe)
    else:
        rs.run_regr(opt.desc, opt.regr, opt.mode, opt.no_build, opt.exe, opt.dump, opt.hash_en, opt.gui_en)
        





##--Legacy code of calling check() as external command
    ##NOTE: For regression, we'd like to add a timeout, but I've tried two solutions and both of 
    ##them are failed. 1. Use multiprocessing.dummy (ThreadPool), but the join() of it is different 
    ##from threading's, it has no timeout parameter; 2. Use multiprocessing pool and ThreadPool, and 
    ##get() of threading pool to set timeout. But since mp.apply_async cannot pickle class type 
    ##function, it also failed. 
    #def async_engine(self, func, desc, sim_cmds, **kw):
    #    
    #    def exe_thd(func, *args, **kw):
    #        timeout = kw.get('timeout', None)
    #        poo = md.Pool(1)
    #        thd = poo.apply_async(func, args=args, kwds=kw)
    #        try:
    #            rtn = thd.get(timeout)
    #            return rtn
    #        except mp.TimeoutError:
    #            pirnt("TIMEOUT")
    #            raise
    #    #p = mp.Pool(maxtasksperchild=1)
    #    #with mp.Pool(processes=len(sim_cmds)) as p
    #    with mp.Pool(maxtasksperchild=1) as p:
    #        for k,v in sim_cmds.items():
    #            thd = partial(exe_thd, func, kw)
    #            p.apply_async(thd, args=[desc,k,v[0],v[1]], kwds=kw,)
    #            
    #            #XXX|Suspicion -- Faliure in callback makes hang
    #            #p.apply_async(thd, args=(desc,k,v[0],v[1]), callback=collectMyResult)
    #            #Strategy.1: Put postproc into callback() or 
    #            #Strategy.2(now using): Put postproc after sim and lock it
    #            #callback=self.callback)

    #    p.close() #turn off Pool to prevent it receive new process
    #    p.join()
    
    #def __dbg_callback_result(self, result):
    #    #print(result)
    #    #'with open' assured to create it
    #    with open(self.regr_result_temp_f, 'a') as f:
    #        f.write(str(result)+'\n')

    #def callback(self, result):
    #    '''
    #    Parameters
    #    ----------
    #    _df : dataframe 
    #        Result from a single process

    #    Returns
    #    -------
    #    '''
    #    max_fsize = 2**30 #bits
    #    self.log.info('[CALLBACK FINISH]%s' %(result))
    #    if(os.path.getsize(self.regr_result_temp_f)< max_fsize): #should be less than 1GB
    #        self.result_df.to_csv(self.regr_result_temp_f, mode='a')
    #    else:
    #        self.log.warning("%s exceeds %s, no write in" %(self.regr_result_temp_f, max_fsize))
    #    return 0
    


##Invoke as an external command is a no-good option
#    def test_postproc(self, desc, group, test_l): 
#        test_pm_f = cdir+'/../'+self.meth_desc['test_pm_home']+self.meth_desc[group+'_pm']
#        if os.environ.get('OUT_CCPERF'):
#            edir = os.environ['OUT_CCPERF']
#        else:
#            edir = self.meth_desc['default_output_home'] %(stem, 'vega20c')
#        pm_cmd = test_pm_f+' -f %s -d %s -e %s -t %s'
#        check = util.call_from_sys(pm_cmd %('check', desc, edir, str(test_l))) 
#        #result = DF("", columns=['check','bottleneck','theory','measure','unit','formula'])
#        return check
            #??Per test check here???
            #invalid_tests.append(t)
            #self.result_df = util.alist2df(self.result_df)([t]+['NA']*(len(regr_col)-1))

