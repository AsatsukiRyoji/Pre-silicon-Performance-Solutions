#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQ-EX Dependency Performance Model
@author: Guo Jiamin
"""
import os, sys, re
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
    'sq_ex_dependency'   : {
        'dv'            : dv_dir + 'perf_sq_ex_dependency.dv'
        ,'test_ptn'     : "perf_sq_ex_(\w+)_\w(\d+)_then_(\w+)_\w(\d+)_dep(\w+)_ipw(\d+)_wpg(\w+)"
        ,'test_param_l' : ['itype1', 'bitwise1', 'itype2', 'bitwise2', 'depend', 'valu', 'wpg']
        ,'warmup'       : 1
    }
}


class SQExDependencyPM(PerfTestPM):
    
    def __init__(self):
        # call the __init__ func of parent class
        super(SQExDependencyPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['sq_ex_dependency'] 
        pass
    
    def theory(self, desc, test = None, gui_en = False, **kw):
        '''SQ VALU Theory
        :test: str(command line) or list or None(default, means every test in dv)
        '''

        super().theory(desc, test, gui_en, **kw)
        meta_col = ['name',
                    'wpg',                                                  # for cp theory
                    'vgpr', 'unorder',                                      # for spi theory
                    'valu', 'depend',                                       # for sq theory 
                    'itype1', 'bitwise1', 'itype2', 'bitwise2'              # for sq theory 
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
        # get meta_df['valu'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']      # for sp using, instead of sq issuing
        
        meta_df['vrate'] = "simd_exec_vop"
        meta_df['bitwise1'] = meta_df['bitwise1'].astype(int)
        meta_df['bitwise2'] = meta_df['bitwise2'].astype(int)
        meta_df['bitwise1'] = meta_df['bitwise1'].astype(str)
        meta_df['bitwise2'] = meta_df['bitwise2'].astype(str)
        meta_df['vrate1'] = meta_df['vrate'].str.cat(meta_df['bitwise1'])
        meta_df['vrate2'] = meta_df['vrate'].str.cat(meta_df['bitwise2'])
        
        inst_classification = {}
        inst_classification['v_add']            = 'normal'
        inst_classification['v_sub']            = 'normal'
        inst_classification['v_and']            = 'normal'
        inst_classification['v_add_co']         = 'normal'
        inst_classification['v_sub_co']         = 'normal'
        inst_classification['v_addc_co']        = 'normal'
        inst_classification['v_subb_co']        = 'normal'
        inst_classification['v_cndmask']        = 'normal'
        inst_classification['v_max']            = 'normal'
        inst_classification['v_min']            = 'normal'
        inst_classification['v_or']             = 'normal'
        inst_classification['v_mov']            = 'normalx4'
        inst_classification['v_lshlrev']        = 'normalx4'
        inst_classification['v_lshrrev']        = 'normalx4'
        inst_classification['v_readlane']       = 'normal'
        inst_classification['v_readfirstlane']  = 'normal'
        inst_classification['v_writelane']      = 'normal'
        inst_classification['v_cmp_eq']         = 'comparation'
        inst_classification['v_cmpx_eq']        = 'comparation'
        inst_classification['v_div_scale']      = 'division'
        inst_classification['v_div_fmas']       = 'division'

        dependency_type = {}
        dependency_type['v_add']                = 'v_read_sgpr_as_constant'
        dependency_type['v_sub']                = 'v_read_sgpr_as_constant'
        dependency_type['v_and']                = 'v_read_sgpr_as_constant'
        dependency_type['v_add_co']             = 'v_write_vcc'
        dependency_type['v_sub_co']             = 'v_write_vcc'
        dependency_type['v_addc_co']            = 'v_read_sgpr_as_carry_in'
        dependency_type['v_subb_co']            = 'v_read_sgpr_as_carry_in'
        dependency_type['v_readlane']           = 'vr_read_sgpr_as_lane_select'
        dependency_type['v_readfirstlane']      = 'vr_read_thread0_as_lane_select'
        dependency_type['v_writelane']          = 'vw_read_sgpr_as_lane_select'
        dependency_type['v_cmp_eq']             = 'v_write_vcc'
        dependency_type['v_div_scale']          = 'division'
        dependency_type['v_div_fmas']           = 'division'
        dependency_type['v_cmpx_eq']            = 'v_write_exec'
        dependency_type['v_mov']                = 'v_write_vgpr'
        dependency_type['v_lshlrev_b32']        = 'v_write_vgpr'
        dependency_type['v_lshrrev_b32']        = 'v_write_vgpr'
        dependency_type['v_cndmask']            = 'v_write_vcc'
        dependency_type['v_max']                = 'v_read_exec'
        dependency_type['v_min']                = 'v_read_exec'
        dependency_type['v_or']                 = 'v_read_exec'
        dependency_type['v_mov']                = 'v_write_vgpr'
        dependency_type['v_lshlrev']            = 'v_write_vgpr'
        dependency_type['v_lshrrev']            = 'v_write_vgpr'
        
        meta_df['dep1'] = meta_df['itype1'].replace(dependency_type)
        meta_df['dep2'] = meta_df['itype2'].replace(dependency_type)

        meta_df['itype1'] = meta_df['itype1'].replace(inst_classification)
        meta_df['itype2'] = meta_df['itype2'].replace(inst_classification)
        
        meta_df['depend_type'] = meta_df['dep1'].str.cat(meta_df['dep2'], sep = "_then_")

        #meta_df.loc[meta_df['depend_type'] == 'v_write_vgpr_then_vr_read_sgpr_as_lane_select', "itype2"] = 'half_rate' # wave/cycle
        
        meta_df['depend_second_condition'] = meta_df['depend_type'].apply(lambda x: 1 if (x in [
                                                                                        "vr_read_sgpr_as_lane_select_then_vr_read_sgpr_as_lane_select", 
                                                                                        "vr_read_sgpr_as_lane_select_then_vw_read_sgpr_as_lane_select", 
                                                                                        "v_write_vcc_then_vr_read_sgpr_as_lane_select", 
                                                                                        "v_write_vcc_then_vw_read_sgpr_as_lane_select", 
                                                                                        "division_then_vr_read_sgpr_as_lane_select", 
                                                                                        "division_then_vw_read_sgpr_as_lane_select", 
                                                                                        "v_write_exec_then_vr_read_sgpr_as_lane_select", 
                                                                                        "v_write_exec_then_vr_read_thread0_as_lane_select", 
                                                                                        "v_write_exec_then_vw_read_sgpr_as_lane_select"]) 
                                                                                      else 0)

        meta_df['depend'] = meta_df['depend'].replace(["true", "false"], [1, 0])
        meta_df['depend'] = meta_df['depend'] | meta_df['depend_second_condition']
        meta_df['depend'] = meta_df['depend'].astype(int)
        
        meta_df['vrate1'] = meta_df['vrate1'].str.cat(meta_df['itype1'], sep = "_")
        meta_df['vrate2'] = meta_df['vrate2'].str.cat(meta_df['itype2'], sep = "_")
        ## sp setting####
        #################
        
        meta_cols = meta_df.columns #it will be changed by CCT
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        
        if gui_en:
            from pmgui import PMGui
            gui = PMGui()
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
    sqvr = SQExDependencyPM()
    if opt.func == 'theory':
        sqvr.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        sqvr.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        sqvr.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

