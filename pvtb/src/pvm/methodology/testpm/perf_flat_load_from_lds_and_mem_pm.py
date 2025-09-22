#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flat_load_from_lds_and_mem Performance Model
FULL_thread - dispatch 2 instructions, 1 access TCC, 1 access LDS
HALF_thread - dispatch 2 instructions, half of the threads in 1 instuctionaccess TCC while the other half access LDS
@author: Gui Yiheng
"""

import os, sys, re
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
    'flat_load_from_lds_and_mem' : {
        'dv'            : dv_dir + 'perf_flat_load_from_lds_and_mem.dv'
        ,'test_ptn'     : "perf_flat_load_from_lds_and_mem_(FULL|HALF)_thread_(hit[a-zA-Z]+)"
        ,'test_param_l' : ['flatldsaccesstype']
        ,'warmup'       : 1

    }
}

class FlatLoadFromLdsandMemPM(PerfTestPM):
    def __init__(self):
        super(FlatLoadFromLdsandMemPM, self).__init__()
        self.test_cfg = testpm_cfg_d['flat_load_from_lds_and_mem']

    def theory(self, desc, test = None, gui_en = False, **kw):
        """Flat_load_from_lds_and_mem Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test)
        rdir = kw.get('rdir', None)
        # for lds access test, we only use the algo-spisq_launch_done_ave to get the performance results
        algo = 'spisq_launch_done_ave'
        #pdb.set_trace()
        # use below test as the reference test
        #test_off = 'perf_buffer_instruction_ls_ooo_OFF'
        test_off = test.replace("HALF", "FULL")
        self.measure(desc, algo, rdir, test_off, gui_en = False, **kw)
         
        self.theo = self.meas
        self.theo['bottleneck'] = 'wavelifetime'    # unit is cycle per wave
        theo_clumns = ['name', 'measure', 'bottleneck', 'unit']
        self.theo = pd.DataFrame(self.theo, columns = theo_clumns)
        self.theo.rename(columns = {'measure': 'theory'}, inplace = True)
        self.theo['name'] = test
        self.meas = DF() #Clean out reference test result for check()

        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo])

        return self.theo

    def measure(self, desc, algo, edir = './', test = None, gui_en = False, **kw):
        """Flat_load_from_lds_and_mem PM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """
        #pdb.set_trace()
        super().measure(desc, algo, edir, test, gui_en, **kw)

    def check(self, desc, edir, test, gui_en = False, **kw):
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
    flflm = FlatLoadFromLdsandMemPM()
    if opt.func == 'theory':
        flflm.theory(opt.desc, opt.test, opt.gui_en, rdir=opt.rdir)
    elif opt.func == 'measure':
        flflm.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        flflm.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

