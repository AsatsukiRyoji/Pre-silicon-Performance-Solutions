#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS read matrix (To VGPR) Performance Model
@author: Lin Yiyu
"""

import os, sys, re
from pandas import DataFrame as DF
import pandas as pd
import pdb

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir + '../')

import utility.util as util
from testpm.perf_test_pm import *
from measure.core_performance_measure import ComputeCoreMeasure as CCM

# test infomation about dv file, pattern, parameter and warm-up
dv_dir = cdir + '/../../shader/'
testpm_cfg_d = {
    'latency_sqc_miss'        : {
        'dv'            : dv_dir + 'perf_sqc_miss.dv'
        ,'test_ptn'     : "perf_sqc_miss_s_(\w+)_ipw(\d+)_wpg(\d+)"
        ,'test_param_l' : ['inst', 'ipw', 'wpg']
        ,'warmup'       : 1
    }
}

class LtcDsPM(PerfTestPM):
    def __init__(self):
        # call the __init__ func of parent class
        super(LtcDsPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['latency_sqc_miss'] 

    def measure(self, desc, algo, edir = './', test = None, gui_en = False, **kw):
        """BUFFER Load (To VGPR) PM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """

        # call the function in perf_test_pm
        super().measure(desc, algo, edir, test, gui_en, **kw)

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = LtcDsPM()
    if opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()


