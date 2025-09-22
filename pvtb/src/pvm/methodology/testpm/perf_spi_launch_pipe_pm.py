#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPI wave launch Performance Model
@author: Guo Jiamin
@modifu: Kan Chengliang
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
    'spi_wave_launch_pipe'       : {
        'dv'            : dv_dir + 'perf_spi_launch_pipe.dv'
        ,'test_ptn'     : "perf_spi_launch_pipe_ipw(\d+)_tg(\d+)_wpg(\d+)_pip(\d+)_pri(\d+)"
        ,'test_param_l' : ['valu', 'tg', 'wpg', 'pip',  'pri']
        ,'warmup'       : 0
    }
}

class SPIWaveLaunchPipePM(PerfTestPM):
    
    def __init__(self):
        # call the __init__ func of parent class
        super(SPIWaveLaunchPipePM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['spi_wave_launch_pipe'] 
        pass
    
    def theory(self, desc, test = None, gui_en = False, **kw):
        '''SPI wave launch  Theory
        :test: str(command line) or list or None(default, means every test in dv)
        '''

        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'tg', 'pip', 'wpg',                                  # for cp theory
                    'sgpr', 'vgpr', 'unord',                      # for spi theory
                    'valu',                                 # for sq theory 
                    ]
        
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)
        
        ################
        ## cp setting###
        # get meta_df['wpg'] by testname with test_info_df
        meta_df['que'] = 1
        meta_df['gpd'] = meta_df['tg']
        if meta_df['pip'][0]==1:
            meta_df = meta_df.drop('pip',axis=1)
        else:
            meta_df['que_send_delay'] = meta_df['pip'].replace([2, 3, 4],["two_pipe", "three_pipe", "four_pipe"])
        ## cp setting###
        ################

        #################
        ## spi setting###
        meta_df['sgpr'] = 1
        meta_df['vgpr'] = 1
        meta_df['unorder'] = 1 
        ## spi setting###
        #################
        
        #################
        ## sp setting####
        # meta_df['vop32'] = meta_df['valu']      # for sp using, instead of sq issuing
        ## sp setting####
        #################
        
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
    cpd = SPIWaveLaunchPipePM()
    if opt.func == 'theory':
        cpd.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        cpd.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        cpd.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()


