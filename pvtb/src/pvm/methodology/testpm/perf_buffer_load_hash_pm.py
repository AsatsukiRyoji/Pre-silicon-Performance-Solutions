#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buffer load (To VGPR) 128 Read Performance Model
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

dv_dir = cdir + '/../../cache/'
testpm_cfg_d = {
    'buffer_load_hash' : {
        'dv'            : dv_dir + 'perf_buffer_load_hash.dv'
        ,'test_ptn'     : "perf_buffer_load_dwordx4_128B_hitTCC_ipw(\d+)_wpg(\d+)_\w+"
        ,'test_param_l' : ['vmem', 'wpg']
        ,'warmup'       : 1
    }
}

class BufferLoadHashPM(PerfTestPM):
    def __init__(self):
        super(BufferLoadHashPM, self).__init__()
        self.test_cfg = testpm_cfg_d['buffer_load_hash']

    def theory(self, desc, test = None, gui_en = False, **kw):
        """ 
        Buffer load (To VGPR) 128 Read HASH Performance Model
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        
        meta_col = ['name',
                    'wpg',                                          # for cp theory
                    'vgpr', 'sgpr', 'unorder',                      # for spi theory
                    'valu', 'salu', 'vmem', 'smem', 'soffset',      # for sq theory 
                    'vop32', 'component', 'vmemPAY',                # for sp theory
                    'vmemCOA',                                      # for ta theory
                    'vmemTER',                                      # for td theory
                    'vmemCAC',                                      # for tcp theory
                    'vmemTYPE'                                      # for tcc theory
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
        meta_df['sgpr']  = 3            # S0 & S1 for get the buffer addr and S2 gets the threadgroup id
        meta_df['unorder'] = 1          # do not use baton
        ## spi setting###
        #################
        
        #################
        ## sq setting####
        meta_df['salu']  = 3            # for buffer load dw, it shoud be 3 at less.
        meta_df['valu']  = 8            # for buffer load dw, it shoud be 8 at less.
        meta_df['smem']  = 1
        meta_df['soffset'] = 1          # for now, we just use buffer inst with Soffset
        
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']
        meta_df['vmemPAY'] = 4
        meta_df['component'] = 1
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        meta_df['vmemCOA'] = 'coalesced'
        ## ta setting####
        #################
        
        #################
        ## td setting####
        meta_df['vmemTER'] = 'vgpr'     # lds or vgpr, for this case, lds is selected
        ## td setting####
        #################       
        
        ##################
        ## tcp setting####
        meta_df['vmemCAC'] = 'TCC'
        ## tcp setting####
        ##################

        ##################
        ## tcc setting####
        meta_df['vmemTYPE'] = 'load'
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
        """BUFFER Load (To VGPR) PM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().measure(desc, algo, edir, test, gui_en, **kw)

    def check(self, desc, edir, test, gui_en = False, **kw):
        '''
        :test: str or list. 
        '''
        super().check(desc, edir, test, gui_en, **kw)

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = BufferLoadHashPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

