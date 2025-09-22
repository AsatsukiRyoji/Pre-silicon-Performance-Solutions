#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CP Dispatch Performance Model
@author: Li Lizhao
@modify: Huang Tianfeng
"""
import os,sys,re
from pandas import DataFrame as DF
import pandas as pd
import pdb
import numpy as np

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir+'../')

import utility.util as util
from testpm.perf_test_pm import *
from theory.core_performance_theory import ComputeCoreTheory as CCT
from measure.core_performance_measure import ComputeCoreMeasure as CCM
from check.core_performance_check import ComputeCoreCheck as CCC

# test infomation about dv file, pattern, parameter and warm-up
dv_dir = cdir + '/../../command/'
testpm_cfg_d = {
    'cp_dc_aql_dispatch'       : {
        'dv'            : dv_dir + 'perf_cp_dc_aql_dispatch.dv'
        ,'test_ptn'     : "perf_cp_dc_aql_dispatch_dpq(\d+)_dimx(\d+)_dimy(\d+)_dimz(\d+)_tpgx(\d+)_wpg(\d+)"
        ,'test_param_l' : ['dpq','dimx','dimy','dimz','tpgx','wpg']
        ,'warmup'       : 0
    }
}

class CPDCAQLDispatchPM(PerfTestPM):
    
    def __init__(self):
        # call the __init__ func of parent class
        super(CPDCAQLDispatchPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['cp_dc_aql_dispatch']
        pass
    

    def theory(self, desc, test=None, gui_en = False, **kw):
        '''CP DISPATCH Theory
        :test: str(command line) or list or None(default, means every test in dv)
        '''

        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'wpg',                                  # for cp theory
                    'valu',                                 # for sq theory 
                    ]
        
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)

        meta_df['valu'] = 32
        meta_df['unorder'] = 1

        meta_cols = meta_df.columns #it will be changed by CCT
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        
        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo], [meta_cols])

        return self.theo


        if type(test) == str:
            try: test = eval(test)  #If it's a str([])
            except: test= [test]
    
    def measure(self, desc, algo, edir, test=None, gui_en = False, **kw):
        """CPDCAQLDispatchPM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """
        #algo = 'cpspi_csdata_mun'
        # call the function in perf_test_pm
        super().measure(desc, algo, edir, test, gui_en, **kw)


    def check(self, desc, edir, test, gui_en = False, **kw):
        '''
        :test: str or list. 
        '''

        # call the function in perf_test_pm
        super().check(desc, edir, test, gui_en, **kw)


if __name__=='__main__':
    opt = util.option_parser()
    cpd = CPDCAQLDispatchPM()
    if opt.func == 'theory':
        cpd.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        cpd.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        cpd.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

