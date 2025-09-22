#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buffer load (To VGPR) Performance Model
@author: Wu Yanting
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
    'buffer_load_burst' : {
        'dv'            : dv_dir + 'perf_buffer_load_burst.dv'
        ,'test_ptn'     : "perf_buffer_([a-z]+)_dwordx(\d)_comp(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)_so(\d+)_tid(\d)_burst(ON|OFF)"
        ,'test_param_l' : ['vmemTYPE', 'vmemPAY', 'component', 'vmemCAC', 'vmem', 'wpg', 'soffset']
        ,'warmup'       : 0
    }
}

class BufferLoadBurstPM(PerfTestPM):
    def __init__(self):
        # call the __init__ func of parent class
        super(BufferLoadBurstPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['buffer_load_burst'] 

    def theory(self, desc, test = None, gui_en = False, **kw):
        """
        Buffer Load Burst (To VGPR) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test)
        rdir = kw.get('rdir', None)
        # for burst test, we only use the algo-tcctcr_rdata_mun to get the performance results
        #algo = 'tcctcr_rdata_mun'
        algo = 'tcctcr_rdata_mun'

        # use below test as the reference test
        burst_off = test.replace("ON", "OFF")
        self.measure(desc, algo, rdir, burst_off, gui_en = False, **kw)

        self.theo = self.meas
        self.theo['bottleneck'] = 'tcctcr_data'
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
        """BUFFER Load (To VGPR) PM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """

        # call the function in perf_test_pm
        super().measure(desc, algo, edir, test, gui_en, **kw)

    def check(self, desc, edir, test, gui_en = False, **kw):
        '''
        :test: str or list. 
        '''
        
        # call the function in perf_test_pm
        super().check(desc, edir, test, gui_en, **kw)
        self.chk_df['check'] = self.chk_df.T.apply(lambda x : 'pass' if x['name'].endswith('OFF') else x['check'])
        if gui_en:
            gui = util.PMGui()
            gui.run([self.chk_df])
        return self.chk_df

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = BufferLoadBurstPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en, rdir=opt.edir)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

