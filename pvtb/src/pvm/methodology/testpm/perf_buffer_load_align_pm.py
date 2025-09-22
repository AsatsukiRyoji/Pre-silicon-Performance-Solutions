#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buffer load (To VGPR) 128 align Read Performance Model
@author: Xiong Jiayun
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
    'buffer_load_align' : {
        'dv'            : dv_dir + 'perf_buffer_load_align.dv'
        ,'test_ptn'     : "perf_buffer_([a-z]+)_dwordx(\d)_comp(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)_align(\d+)_soffset(\d+)"
        ,'test_param_l' : ['vmemTYPE', 'vmemPAY', 'component', 'vmemCAC', 'vmem', 'wpg','align','soffset']
        ,'warmup'       : 1
    }
}

class BufferLoadAlignPM(PerfTestPM):
    def __init__(self):
        super(BufferLoadAlignPM, self).__init__()
        self.test_cfg = testpm_cfg_d['buffer_load_align']

    def theory(self, desc, test = None, gui_en = False, **kw):
        """ 
        Buffer load (To VGPR) 128 Read ALIGN Performance Model
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'wpg',                                          # for cp theory
                    'vgpr', 'sgpr', 'unorder',                      # for spi theory
                    'valu', 'salu', 'vmem', 'smem', 'soffset',      # for sq theory 
                    'vop32', 'component', 'vmemPAY',                # for sp theory
                    'vmemCOA',                                      # for ta theory
                    'coaRATIO',                                     # for ta theory
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
                0 if (re.match("perf_buffer_([a-z]+)_dwordx(\d)_comp(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)_align(\d+)_soffset0", x)) else 1)
        
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']
        #meta_df['vmemPAY'] = 4
        meta_df['component'] = 1
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        meta_df['vmemCOA'] = 'coalesced'               
        #meta_df['vmemCOA'] = meta_df['name'].apply(lambda x: 
        #    'uncoalesced' if (re.match("perf_buffer_load_dwordx2_comp1_\w+", x)) else 'coalesced')
        #align = self.test_info_df.loc[0,'align']
        #dwordx = self.test_info_df.loc[0,'vmemPAY']
        def serach_keywoard(test):
            align_pattern = r'align(\d+)'
            match = re.search(align_pattern,test)
            if match:
                return match.group(1)
        meta_df['coaRATIO'] = meta_df['name'].apply(lambda x: 
            serach_keywoard(x))

        def judge_ratio(align,dwordx):
            if align == 128:
                return 1
            elif dwordx == 2:     
                return 0.5
            elif align == 64:            
                return 0.667
            elif 0<align and align<64 and dwordx == 1:            
                return 0.625
            elif 0<align and align<64 and dwordx == 4:            
                return 0.654
            elif 64<align and align<128 and dwordx == 1:            
                return 0.625
            elif 64<align and align<128 and dwordx == 4: 
                return 0.531
        def judge_coa(align,dwordx):
            if align == 128:
                return 'coalesced'
            elif dwordx == 2:     
                #return 'uncoalesced' TODO, maybe TA and TC coa are not same
                return 'coalesced'
            else:     
                return 'coalesced'
        for index, row in meta_df.iterrows():
            meta_df.loc[index,'coaRATIO'] = judge_ratio(int(row['coaRATIO']),int(row['vmemPAY']))
            meta_df.loc[index,'vmemCOA'] = judge_coa(int(row['coaRATIO']),int(row['vmemPAY']))
        #print('[XIONG_DEBUG] vmemCOA,coaRATIO,vmemPAY,soffset: \n',meta_df['vmemCOA'],meta_df['coaRATIO'],meta_df['vmemPAY'],meta_df['soffset'])
        
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
        #print('[XIONG_DEBUG] meta_df:\n',meta_df) 
        meta_cols = meta_df.columns #it will be changed by CCT
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        #print('[XIONG_DEBUG] self.theo:\n',self.theo)
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
    buflv = BufferLoadAlignPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

