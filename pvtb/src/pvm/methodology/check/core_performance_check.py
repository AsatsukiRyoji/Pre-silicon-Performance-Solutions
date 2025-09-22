#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Performance Check Model
@author: Li Lizhao
"""
import os,sys, pdb, re
from pandas import DataFrame as DF
import pandas as pd
import numpy as np

cdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cdir+'/../')
sys.path.append(cdir+'/')

from utility import util
import bowen_b0_waive_list
# The keys is bottleneck and the value is measure algorithm
# if there are more than one candidates of bottleneck, CPVM should choose
# first one as bottleneck, and correspondingly the measure algorithm of it 
# is choosed.
check_meas_map = {
    'tcrtcc_data'       : 'tcrtcc_wdata_mun'
    ,'dispatch_wave'    : 'cpspi_csdata_muu'
    ,'alloc_wave_resource' : 'spisq_launch'
    ,'baton_limit'      : 'spisq_launch'
    ,'init_vgpr'        : 'spisp_vdata'
    ,'init_sgpr'        : 'spisq_sdata'
    ,'spisq_cmd'        : 'spisq_launch'
    ,'tcctcr_data'      : 'tcctcr_rdata_mun'
    ,'tdsp_data'        : 'tdsp_data_mun'
    ,'ldssp_read_data'  : 'ldssp_read_mun'
    ,'splds_idx'        : 'splds_idx_mun'
    ,'lds_latency'      : 'lds_latency_mun'
    ,'sq_pick_valu'     : 'sqsp_simd_cmd'
    ,'sp_exec'          : 'spsq_done'
    ,'sqsp_simd_src_d'  : 'sqsp_simd_src_d_mun'
    ,'sqsp_simd_src_c' : 'sqsp_simd_src_c_mun'
    ,'tatcp_addr'       : 'tatcp_addr'
    ,'tcptd_data'       : 'tcptd_data_mun'
    ,'sqta_cmd'         : 'sqta_cmd'
    ,'wavelifetime'     : 'spisq_launch_done_ave'
    ,'wavelifetime_idv' : 'spisq_launch_done_idv'
    ,'sxgds_data'       : 'sxgds_data_mun'
    ,'gds_latency'      : 'gds_latency_muu'
    ,'eatcc_data'       : 'eatc_rdret_mun'
    ,'default'          : 'spisq_launch'
}

class ComputeCoreCheck:

    def __init__(self, desc, meta_df):
        self.chk_range = {'floor': .85, 'ceiling': 1., 'ref_floor': .15, 'ref_ceiling': 10.}
        self.meta = meta_df

    ##def theory_vs_measure(self, cmp_se, is_ref=False, algo=None):
    def theory_vs_measure(self, cmp_se, is_ref=False, algo=None, is_latency=False):
        '''
        :cmp_se: pandas.Series. One test row
        '''
        #pdb.set_trace()
        if is_ref:
            floor,ceiling = self.chk_range['ref_floor'], self.chk_range['ref_ceiling']
        else:
            floor,ceiling = self.chk_range['floor'], self.chk_range['ceiling']
        is_waived = False
        
        ##Rectify floor and ceiling if it's waived test
        for k,v in bowen_b0_waive_list.waive_list.items():
            try:
                if re.search(r''+k+'', cmp_se['name']):
                    is_waived = True

                    if is_ref:
                        floor, ceiling = v['ref_floor'], v['ref_ceiling']
                    else:
                        floor, ceiling = v['floor'], v['ceiling']
                    
                    break;
            except:
                continue

        if cmp_se['measure'] != 'TBD' and cmp_se['measure'] != 'nan':
            t, m = float(cmp_se['theory']), float(cmp_se['measure'])
            if is_ref:
                if algo == 'wavelifetime' or algo == 'wavelifetime_idv':
                    if m/t <= 1-floor and m/t >= 1/ceiling:
                        check = 'pass'
                    else:
                        check = 'fail'
                elif algo == 'tcrtcc_data' or algo == 'tcctcr_data': # burst performance 
                    if m/t > 0.95: # TODO: confirm the value
                        check = 'pass'
                    else:
                        check = 'fail'
            elif is_waived:
                if m/t < floor:
                    check = 'underfail'
                elif m/t > ceiling:
                    check = 'overfail'
                else:
                    check = 'pass'
            else:
                if is_latency:
                    if abs(t-m)/min(t,m) <= 1- floor:
                        check = 'pass'
                    else:
                        check = 'fail'
                else:
                    if m/t >= floor and m/t <= ceiling:
                        check = 'pass'
                    else:
                        check = 'fail'

            ##tests need check channel_risk. True:test has chn risk.
            if 'channel_risk' in cmp_se.index:
                if cmp_se['channel_risk'] == 'Have_Risk':
                    check = 'fail'
                else:
                    check = check
            else:
                check = check

            if is_latency:
                return str((check,round((1 - abs(t-m)/min(t,m)),3)))
            else:
                return str((check,round(m/t,3)))

        else:
            return str(('invalid',-1))

    def get_chk(self, is_ref=False, algo=None, is_latency=False):
        m = self.meta
        m['check'] = m.T.apply(lambda x: self.theory_vs_measure(x, is_ref, algo, is_latency))
        m['ratio'] = m['check']
        ##eval(x) return a tuple
        m['check'] = m['check'].apply(lambda x: eval(x)[0])
        m['ratio'] = m['ratio'].apply(lambda x: eval(x)[1])
        self.meta = m
        return self.meta

