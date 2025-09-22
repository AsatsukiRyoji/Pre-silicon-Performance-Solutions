#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP Valu Performance Model
@author: Guo Shihao
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

# perf_sp_v_mmac_f32_16x16x16_bf16_lit0_lts0_data_forward_true_ipw256_wpg8
# test infomation about dv file, pattern, parameter and warm-up
dv_dir = cdir + '/../../shader/'
testpm_cfg_d = {
    'sp_valu_gemm'       : {
        'dv'            : dv_dir + 'perf_sp_valu_gemm.dv'
        ,'test_ptn'     : "perf_sp_v_(mmac_\\w+x\\d+)_(f64|f32|tf32|f16|bf16|fp8_fp8|bf8_bf8|fp8_bf8|bf8_fp8|u4|i4|u8|i8)_.*lts[0,1]_data_forward_\\w+_ipw(\\d+)_wpg(\\d+)"
        ,'test_param_l' : ['itype', 'bitwise', 'valu', 'wpg']
        ,'warmup'       : 1
    }
}


class SPValuGemmPM(PerfTestPM):
    
    def __init__(self):
        # call the __init__ func of parent class
        super(SPValuGemmPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['sp_valu_gemm'] 
        pass
    
    def theory(self, desc, test = None, gui_en = False, **kw):
        '''SP VALU Theory
        :test: str(command line) or list or None(default, means every test in dv)
        '''

        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'wpg',                                                  # for cp theory
                    'vgpr', 'unorder',                                  # for spi theory
                    'valu', 'itype', 'bitwise',                             # for sq theory 
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
        meta_df['vrate'] = "simd_exec"
        meta_df['vrate'] = meta_df['vrate'].str.cat(meta_df['itype'], sep="_")
        meta_df['vrate'] = meta_df['vrate'].str.cat(meta_df['bitwise'], sep="_")
        meta_df['m'] = meta_df['itype'].apply(lambda x: int((re.search('.*_(\d+)x\d+x\d+', x).group(1))))
        meta_df['n'] = meta_df['itype'].apply(lambda x: int((re.search('.*_\d+x(\d+)x\d+', x).group(1))))
        meta_df['k'] = meta_df['itype'].apply(lambda x: int((re.search('.*_\d+x\d+x(\d+)', x).group(1))))
        meta_df['total_flops'] = meta_df['m'] * meta_df['n'] * meta_df['k'] * 2 / 64
        meta_df['freq'] = meta_df['name'].apply(lambda x: 
                1.36 if (re.match(".*\d+_f(64|32)_.*", x)) else 1.25)
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
    cpd = SPValuGemmPM()
    if opt.func == 'theory':
        cpd.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        cpd.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        cpd.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()


