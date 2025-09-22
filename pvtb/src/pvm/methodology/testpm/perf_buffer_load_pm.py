#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buffer load (To VGPR) Performance Model
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
dv_dir = cdir + '/../../cache/'
testpm_cfg_d = {
    'buffer_load'       : {
        'dv'            : dv_dir + 'perf_buffer_load.dv'
        ,'test_ptn'     : "perf_buffer_([a-z]+)_dwordx(\d)_comp(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)_so(\d+)_tid\d"
        ,'test_param_l' : ['vmemTYPE', 'vmemPAY', 'component', 'vmemCAC', 'vmem', 'wpg', 'soffset']
        ,'warmup'       : 1
    }
}

class BufferLoadPM(PerfTestPM):
    def __init__(self):
        # call the __init__ func of parent class
        super(BufferLoadPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['buffer_load'] 

    def theory(self, desc, test = None, gui_en = False, **kw):
        """
        Buffer Load (To VGPR) Theory
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
        meta_df['soffset'] = meta_df['name'].apply(lambda x: # for now, we can choose use soffset or not
                0 if (re.match("perf_buffer_([a-z]+)_dwordx(\d)_comp(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)_so0_\w+", x)) else 1)
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']      # for sp using, instead of sq issuing
        # get meta_df['vmemPAY'] by testname with test_info_df
        # get meta_df['component'] by testname with test_info_df
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        # All is coallesced EXCEPT dwx2 and comp2, it should be seen as uncoalesced scenario with low perf rate
        meta_df['vmemCOA'] = meta_df['name'].apply(lambda x: 
            'uncoalesced' if (re.match("perf_buffer_load_dwordx2_comp[02]_\w+", x)) else 'coalesced')
        ## ta setting####
        #################
        
        #################
        ## td setting####
        meta_df['vmemTER'] = 'vgpr' # lds or vgpr, for this case, lds is selected
        ## td setting####
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
    buflv = BufferLoadPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

