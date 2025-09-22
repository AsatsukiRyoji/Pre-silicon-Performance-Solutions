#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global atomic (To VGPR) Performance Model
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
    'global_atomic'      : {
        'dv'            : dv_dir + 'perf_global_atomic.dv'
        ,'test_ptn'     : "perf_global_atomic_(\w+)_ipw(\d+)_wpg(\d+)"
        ,'test_param_l' : ['vmemPAY', 'vmem', 'wpg']
        ,'warmup'       : 1
    }
}

class GlobalAtomicPM(PerfTestPM):
    
    def __init__(self):
        super(GlobalAtomicPM, self).__init__()
        self.test_cfg = testpm_cfg_d['global_atomic']
    
    def theory(self, desc, test = None, gui_en = False, **kw):
        """Global Atomic (To VGPR) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        
        meta_col = ['name',
                    'wpg', 
                    'vgpr', 'sgpr', 'unorder',                      # for spi theory
                    'valu', 'salu', 'vmem', 'smem', 
                    'vop32', 
                    'vmemPAY', 
                    'vmemTER',                 # for td theory
                    'vmemCAC',
                    'vmemTYPE'
                    ]

        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)
        
        ################
        ## cp setting###
        # get meta_df['wgp'] by testname with test_info_df
        ## cp setting###
        ################
        

        #################
        ## spi setting###
        meta_df['vgpr']  = 1            # thread_id in V0 is needed to control addr
        meta_df['sgpr']  = 3            # S0 & S1 for get the buffer addr and S2 gets the threadgroup id
        meta_df['unorder'] = 1          # do not use baton
        ## spi setting###
        #################
        
        #################
        ## sq setting####
        meta_df['salu']  = 1            # for global load dw, it shoud be 3 at less.
        meta_df['valu']  = 10            # for global load dw, it shoud be 8 at less.
        meta_df['smem']  = 1
        meta_df['soffset'] = 0          # For global opcode the value of soffset is 0
        
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']
        meta_df['vmemPAY'] = meta_df['vmemPAY'].replace(["f32","f32x4","f64","f64x2"], [1, 4, 2, 4])
        meta_df['component'] = 1
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        meta_df['vmemCOA'] = 'uncoalesced'
        ## ta setting####
        #################
        
        #################
        ## td swizzle setting####
        meta_df['vmemTER'] = 'vgpr'
        ## td swizzle setting####
        #################

        ##################
        ## tcp setting####
        # get meta_df['vmemPAY'] by testname with test_info_df
        meta_df['vmemCAC'] = "TCC"
        ## tcp setting####
        ##################

        ##################
        ## tcc setting####
        meta_df['vmemTYPE'] = "atomic"
        ## tcc setting####
        ##################
        
        meta_cols = meta_df.columns #it will be changed by CCT
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo], [meta_cols])
        #print(self.theo)
        return self.theo
    
    def measure(self, desc, algo, edir = './', test = None, gui_en=False, **kw):
        """GLOBAL Atomic (To VGPR) PM Measure
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
        
        super().check(desc, edir, test, gui_en, **kw)
        return self.chk_df

if __name__ == '__main__':
    opt = util.option_parser()
    gapm = GlobalAtomicPM()
    if opt.func == 'theory':
        gapm.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        gapm.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        gapm.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

