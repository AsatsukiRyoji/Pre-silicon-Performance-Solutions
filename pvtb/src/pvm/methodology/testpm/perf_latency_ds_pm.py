#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS read matrix (To VGPR) Performance Model
@author: Guo Jiamin
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
dv_dir = cdir + '/../../shader/'
testpm_cfg_d = {
    'latency_ds'        : {
        'dv'            : dv_dir + 'perf_latency_ds.dv'
        ,'test_ptn'     : "perf_latency_ds_(\w+)_ipw(\d+)_wpg(\d+)"
        ,'test_param_l' : ['lds_inst_type', 'ds_inst', 'wpg']
        ,'warmup'       : 1
    }
}

class LtcDsPM(PerfTestPM):
    def __init__(self):
        # call the __init__ func of parent class
        super(LtcDsPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['latency_ds'] 

    def theory(self, desc, test = None, gui_en = False, **kw):
        """
        DS read matrix (To VGPR) Performance Model
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        
        meta_col = ['name',
                    'wpg',                                              # for cp theory
                    'vgpr', 'unorder',                                  # for spi theory
                    'valu',                                             # for sq theory
                    'vop32',                                            # for sp theory
                    'lds_inst_type', 'ds_inst', 'lds_latency_inst', 'lds_latency_vaule'  # for lds theory
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
        meta_df['valu']  = 1            # for buffer load dw, it shoud be 8 at less.
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32']    = meta_df['valu']       # for sp using, instead of sq issuing

        #################
        ##lds_ltc setting####
        lds_ltc = {}
        lds_ltc['read_b32']  = 'lds_read_b32_latency';
        lds_ltc['write_b64'] = 'lds_write_b64_latency';
        lds_ltc['and_b32']   = 'lds_and_b32_latency';
        meta_df['lds_latency_inst'] = meta_df['lds_inst_type'].replace(lds_ltc)
       
        #hardware issue,needs to add in cfg.
        ## lds_ltc setting####
        #################
        
        meta_cols = meta_df.columns #it will be changed by CCT
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        
        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo], [meta_cols])

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

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = LtcDsPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

