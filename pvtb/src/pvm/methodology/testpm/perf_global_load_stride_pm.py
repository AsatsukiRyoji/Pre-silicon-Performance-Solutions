#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global stride (To VGPR) Performance Model
@author: Gui yiheng
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
    'global_load_stride'      : {
        'dv'            : dv_dir + 'perf_global_load_stride.dv'
        ,'test_ptn'     : "perf_global_([a-z]+)_dwordx(\d)_(hit[a-zA-Z]+)_ipw(\d+)_wpg(\d+)_tci(\d+)_inst0_bankhash(\d+)_stride(\d+)_isize(\d+)"
        ,'test_param_l' : ['vmemTYPE', 'vmemPAY', 'vmemCAC', 'vmem', 'wpg', 'tci']
        ,'warmup'       : 2
    }
}

class GlobalStridePM(PerfTestPM):
    
    def __init__(self):
        super(GlobalStridePM, self).__init__()
        self.test_cfg = testpm_cfg_d['global_load_stride']
    
    def theory(self, desc, test = None, gui_en = False, **kw):
        """Global Stride (To VGPR) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        
        meta_col = ['name',
                    'wpg',
                    'tci',
                    'vgpr', 'sgpr', 'unorder',                      # for spi theory
                    'valu', 'salu', 'vmem', 'smem', 
                    'vop32', 
                    'coaRATIO',
                    'vmemPAY', 
                    'vmemTER',                 # for td theory
                    'vmemCAC',
                    'vmemTYPE'
                    ]

        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)
        #pdb.set_trace() 
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
        meta_df['salu']  = 3            # for global stride dw, it shoud be 3 at less.
        meta_df['valu']  = 8            # for global stride dw, it shoud be 8 at less.
        meta_df['smem']  = 1
        meta_df['soffset'] = 0          # For global opcode the value of soffset is 0
        
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']
        # get meta_df['vmemPAY'] by testname with test_info_df
        meta_df['component'] = 1
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        meta_df['vmemCOA'] = 'coalesced'
        def judge_ratio(tci,dwordx):
            return 0.5 if (tci*dwordx*4)%128>0 else 1
        for index, row in meta_df.iterrows():
            meta_df.loc[index,'coaRATIO'] = judge_ratio(int(row['tci']),int(row['vmemPAY']))
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
        # get meta_df['vmemCAC'] by testname with test_info_df
        ## tcp setting####
        ##################

        ##################
        ## tcc setting####
        # get meta_df['vmemTYPE'] by testname with test_info_df
        ## tcc setting####
        ##################
        
        
        """        
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(test_info_df.loc[:,meta_col], columns = meta_col)
        meta_df['vgpr']  = 1            # thread_id in V0 is needed to control addr
        meta_df['sgpr']  = 3            # S0 & S1 for get the buffer addr and S2 gets the threadgroup id
        meta_df['salu']  = 99           # [TODO] templarily use a max value of all buffer load test due to salu issue is not the bottelneck
        meta_df['valu']  = 105          # [TODO] templarily use a max value of all buffer load test due to valu issue is not the bottelneck

        meta_df['vop32'] = meta_df['valu']

        #vmem
        meta_df['vmemTER'] = 'lds'      # [FIXME] Wrong value, and should be vgpr, but meet error if so
        meta_df['vmemPAY'] = meta_df['vmemPAY'].apply(lambda x: 1 if pd.isnull(x) else x)
        meta_df['vmemPAY'] = meta_df['vmem'] * meta_df['vmemPAY']

        # s_load_dwordx4 load constant from memory to SQC, the test uses warm-up waves to assure 
        # it's already loaded. So only the issue(from sq to sqc) of it is calculated
        meta_df['smem']  = 1
        """
        
        meta_cols = meta_df.columns #it will be changed by CCT
        #pdb.set_trace()
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        if gui_en:
            gui = util.PMGui()
            gui.run([self.theo], [meta_cols])
        #print(self.theo)
        return self.theo
    
    def measure(self, desc, algo, edir = './', test = None, gui_en=False, **kw):
        """GLOBAL STRIDE (To VGPR) PM Measure
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
    glpm = GlobalStridePM()
    if opt.func == 'theory':
        glpm.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        glpm.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        glpm.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

