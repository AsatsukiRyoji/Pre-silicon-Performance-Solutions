#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP Valu Performance Model
@author: Ma Xinging
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
dv_dir = cdir + '/../../shader/'
testpm_cfg_d = {
    'sp_valu_edc'   : {
        'dv'            : dv_dir + 'perf_sp_valu_edc.dv'
        ,'test_ptn'     : "perf_sp_valu_(\w+)_[a-z]+(\d+)_ipw(\d+)_wpg(\d+)_edc(\w+)" #need to update
        ,'test_param_l' : ['itype', 'bitwise', 'valu', 'wpg', 'edc']
        ,'warmup'       : 1
    }
}


class SPValuEdcPM(PerfTestPM):
     
    def __init__(self):
        # call the __init__ func of parent class
        super(SPValuEdcPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['sp_valu_edc'] 
        pass

    def theory(self, desc, test = None, gui_en = False, **kw):
        '''SP VALU Theory
        :test: str(command line) or list or None(default, means every test in dv)
        '''

        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'wpg',                                                  # for cp theory
                    'vgpr', 'unorder',                                  # for spi theory
                    'valu', 'itype', 'bitwise', 'edc',                             # for sq theory 
                    ]
        
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)
        
        ################
        ## cp setting###
        # get meta_df['wpg'] by testname with test_info_df
        ## cp setting###
        ################

        #################
        ## spi setting###
        meta_df['vgpr']  = 1            # thread_id in V0 is needed to control addr
        meta_df['unorder'] = 1          # do not use baton
        ## spi setting###
        #################
        
        #################
        ## sq setting####
        #meta_df['salu']     = 1            # for buffer load dw, it shoud be 3 at less.
        # get meta_df['valu'] by testname with test_info_df  = 8            
        #meta_df['smem']     = 0
        #meta_df['soffset']  = 0          # for now, we just use buffer inst with Soffset
        #meta_df['vmem'] = 0
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']      # for sp using, instead of sq issuing
        meta_df['bitwise'] = meta_df['bitwise'].astype(int)
        meta_df['bitwise'] = meta_df['bitwise'].astype(str)
        meta_df['vrate'] = "simd_exec_vop"
        meta_df['vrate'] = meta_df['vrate'].str.cat(meta_df['bitwise'])
        #meta_df['vrate'] = meta_df['edc'].apply(lambda x: "simd_exec_vop16_normal_edc_on" if x == "ON" else "simd_exec_vop16_normal")
        meta_df['vrate'] = meta_df['name'].apply(lambda x: "simd_exec_vop32_cvt_edc_" if ("cvt" in str(x)) else "simd_exec_vop16_normal_edc_")
        meta_df['vrate'] = meta_df['vrate'].str.cat(meta_df['edc'].str.lower())

        meta_df['freq'] = 1.36
        meta_df['total_flops'] = meta_df['itype'].apply(lambda x: 2 if x == "fma" else 1)


        #meta_df['vrate'] = meta_df['vrate'].str.cat(meta_df['itype'], sep="_")
        
        # get meta_df['vmemPAY'] by testname with test_info_df
        # get meta_df['component'] by testname with test_info_df
        ## sp setting####
        #################
        
        ##################
        ## tcp setting####
        # get meta_df['vmemPAY'] by testname with test_info_df
        # get meta_df['vmemCAC'] by testname with test_info_df
        ## tcp setting####
        ##################

        ##################
        ## tcc setting####
        # get meta_df['vmemTYPE'] by testname with test_info_df
        ## tcc setting####
        ##################
        
        meta_cols = meta_df.columns #it will be changed by CCT
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        
        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo], [meta_cols])

        return self.theo

    def measure(self, desc, algo, edir = './', test = None, gui_en = False, **kw):
        """SPValuPM Measure
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

if __name__=='__main__':
    opt = util.option_parser()
    spve = SPValuEdcPM()
    if opt.func == 'theory':
        spve.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        spve.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        spve.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()


