#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global load/store (To VGPR) with ooo Performance Model
@author: Ma Xingxing
"""
import os,sys,re
from pandas import DataFrame as DF
import pandas as pd
import pdb

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir + '../')

import utility.util as util

from testpm.perf_test_pm import *
from theory.core_performance_theory import ComputeCoreTheory as CCT
from measure.core_performance_measure import ComputeCoreMeasure as CCM
from check.core_performance_check import ComputeCoreCheck as CCC

# test infomation about dv file, pattern, parameter and warm-up
dv_dir = cdir + '/../../cache/'
testpm_cfg_d = {
    'global_ooo'      : {
        'dv'            : dv_dir + 'perf_global_ooo.dv'
        ,'test_ptn'     : "perf_global_\w+_instruction_mtype_\w+_ls_ooo_(ON|OFF)"
        ,'test_param_l' : ['oootype']
        ,'warmup'       : 1
    }
}

class GlobalOooPM(PerfTestPM):
    
    def __init__(self):
        super(GlobalOooPM, self).__init__()
        self.test_cfg = testpm_cfg_d['global_ooo']
    
    def theory(self, desc, test = None, gui_en = False, **kw):
        """Global Ooo (To VGPR) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test)
        rdir = kw.get('rdir', None)
        # for ooo test, we only use the algo-spisq_launch_done_ave to get the performance results
        algo = 'spisq_launch_done_ave'
        
        # use below test as the reference test
        #test_off = 'perf_global_instruction_ls_ooo_OFF'
        test_off = test.replace("ON", "OFF")
        self.measure(desc, algo, rdir, test_off, gui_en = False, **kw)
        
        self.theo = self.meas
        self.theo['bottleneck'] = 'wavelifetime'
        theo_clumns = ['name', 'measure', 'bottleneck', 'unit']
        self.theo = pd.DataFrame(self.theo, columns = theo_clumns)
        self.theo.rename(columns = {'measure': 'theory'}, inplace = True)
        self.theo['name'] = test
        self.meas = DF() #Clean out reference test result for check()

        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo])

        return self.theo
    
    def measure(self, desc, algo, edir = './', test = None, gui_en=False, **kw):
        """GLOBAL Load (To VGPR) PM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().measure(desc, algo, edir, test, gui_en, **kw)

    def check(self, desc, edir, test, gui_en=False, **kw):
        '''
        :test: str or list. 
        '''
        super().check(desc, edir, test, **kw)
        self.chk_df['check'] = self.chk_df.T.apply(lambda x : 'pass' if x['name'].endswith('OFF') else x['check'])
        if gui_en:
            gui = util.PMGui()
            gui.run([self.chk_df])
        return self.chk_df

if __name__ == '__main__':
    opt = util.option_parser()
    gopm = GlobalOooPM()
    if opt.func == 'theory':
        gopm.theory(opt.desc, opt.test, opt.gui_en, rdir=opt.rdir)
    elif opt.func == 'measure':
        gopm.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        gopm.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

