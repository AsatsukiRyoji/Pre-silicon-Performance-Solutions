#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matrix copy (To VGPR) Performance Model
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
    'matrix_copy' : {
        'dv'            : dv_dir + 'perf_matrix_copy.dv'
        ,'test_ptn'     : "perf_matrix_copy_b(\d+)_sw([A-Z]+)_r[A-Z]+_t[A-Z]+_ipw(\d+)"
        ,'test_param_l' : ['vmemTYPE', 'vmemBPE', 'vmemSW', 'vmem']
        ,'warmup'       : 1
    }
}

class MatrixCopyPM(PerfTestPM):
    def __init__(self):
        super(MatrixCopyPM, self).__init__()
        self.test_cfg = testpm_cfg_d['matrix_copy']

    def theory(self, desc, test = None, gui_en = False, **kw):
        """Matrix Copy (To VGPR) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'wpg',                                          # for cp theory
                    'vgpr', 'sgpr', 'unorder',                      # for spi theory
                    'valu', 'salu', 'vmem', 'smem', 'soffset',      # for sq theory 
                    'vop32', 'component', 'vmemPAY',                # for sp theory
                    'vmemCOA',                                      # for ta theory
                    'vmemTER', 'vmemBPE', 'vmemSW',                 # for td theory
                    'vmemCAC',                                      # for tcp theory
                    'vmemTYPE'                                      # for tcc theory
                    ]
        
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)
        
        ################
        ## cp setting###
        meta_df['wpg']  = 4
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
        meta_df['smem']  = 6
        meta_df['soffset'] = 0          # for now, we just use buffer inst with Soffset
        
        #meta_df['vmem']  = 12
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']
        meta_df['vmemPAY'] = 4
        meta_df['vmemTYPE'] = 'load'
        meta_df['component'] = 0
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        ## when r == t matrix_copy_b16 swON to vgpr the address can't be contious so the TCP can't send 128B request
        ## when r != t and stride 32 element matrix_copy_b16 swON to vgpr the address can be contious and the TCP can send 128B request
        meta_df['vmemCOA'] = meta_df['name'].apply(lambda x: 
                'uncoalesced' if ((re.match("perf_matrix_load_b16_swON_rCOL_tCOL\w+", x)) or (re.match("perf_matrix_load_b16_swON_rROW_tROW\w+", x))) else 'coalesced')
        ## ta setting####
        #################
        
        #################
        ## td swizzle setting####
        meta_df['vmemTER'] = 'vgpr'
        ## td swizzle setting####
        #################

        ##################
        ## tcp setting####
        # set meta_df['vmemPAY'] in sp setting
        meta_df['vmemCAC'] = "TCC"
        ## tcp setting####
        ##################

        ##################
        ## tcc setting####
        meta_df['vmemTYPE'] = "load"
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
    mcp = MatrixCopyPM()
    if opt.func == 'theory':
        mcp.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        mcp.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        mcp.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

