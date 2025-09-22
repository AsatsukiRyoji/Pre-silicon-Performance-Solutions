#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Performance Measure Model
@author: Li Lizhao
"""
import os,sys,re, pdb
from collections import OrderedDict as OD
from pandas import DataFrame as DF
import pandas as pd

cdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cdir)
sys.path.append(cdir+'../')

from utility import util
from measure_lib.shader_measure import *
from measure_lib.cache_measure import *
from measure_lib.command_measure import *

class ComputeCoreMeasure:

    def __init__(self, desc, meta_df):
        self.desc = util.get_desc(desc, 'measure')
        self.meta = meta_df
        self.meas = DF(meta_df)
        pass

    @staticmethod
    def get_meas_(algo, attr, edir=None, desc=None, warmup=1):
        not_check_chn_rsk_l = ['pfct_tcc_bfld_interface_measure','tcea_latency_measure','sqsp_simd_cmd_interface_measure','spsq_excp_interface_measure','sqc_interface_hit_measure','sqc_interface_miss_measure','tcptcr_latency_read','tcptcr_latency_write','tcea_rd_latency','op_lds_latency']
        algo_l = algo.split(',') if len(algo)>1 else algo
        attr_l = []
        for a in algo_l:
            algo_ = util.measure_algo_d.get(a)
            if desc != None and edir != None:
                if attr=='measure':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    if 'merge' in algo_['algorithm']:
                        attr_l.append(str(round(rate_d['rate'], 4)))
                    elif 'average' in algo_['algorithm']:
                        attr_l.append(str(round(rate_d['ave_cycle'], 2)))
                    elif 'latency' in algo_['algorithm']:
                        ##attr_l.append(str(round(rate_d['rate'], 2)))
                        attr_l.append(str(round(rate_d['latency'], 2)))
                    elif 'separate' in algo_['algorithm']:
                        attr_l.append('NYI')
                    elif 'pfct' in algo_['algorithm']:
                        attr_l.append(str(round(rate_d['rate'], 4)))
                elif attr=='channel_risk':
                    if any(a == algo_['measure'] for a in not_check_chn_rsk_l):
                        attr_l.append('TBD')
                    else:
                        rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                        attr_l.append(str(rate_d['channel_risk']))
                elif attr=='winratio':
                    #if ('average' or 'latency') in algo_['algorithm']:
                    if any(a in algo_['algorithm'] for a in ['average', 'latency']):
                        attr_l.append('TBD')
                    else:
                        rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                        attr_l.append(str(round(rate_d['winratio'], 3)))
                elif attr=='reqratio':
                    #if ('average' or 'latency') in algo_['algorithm']:
                    if any(a in algo_['algorithm'] for a in ['average', 'latency']):
                        attr_l.append('TBD')
                    else:
                        rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                        attr_l.append(str(round(rate_d['reqratio'], 3)))
                elif attr=='absolute_cycle':
                    #if ('average' or 'latency') in algo_['algorithm']:
                    if any(a in algo_['algorithm'] for a in ['average', 'latency']):
                        attr_l.append('TBD')
                    else:
                        rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                        attr_l.append(str(rate_d['absolute_cycle']))
                elif attr=='absolute_req':
                    #if ('average' or 'latency') in algo_['algorithm']:
                    if any(a in algo_['algorithm'] for a in ['average', 'latency']):
                        attr_l.append('TBD')
                    else:
                        rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                        attr_l.append(str(rate_d['absolute_req']))
                elif attr=='ave_latency':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['ave_latency']))
                elif attr=='median_latency':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['median_latency']))
                elif attr=='max_latency':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['max_latency']))
                elif attr=='min_latency':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['min_latency']))
                elif attr=='max_inst_id':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['max_inst_id']))
                elif attr=='max_dbg_id':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['max_dbg_id']))
                elif attr=='median_inst_id':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['median_inst_id']))
                elif attr=='median_dbg_id':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['median_dbg_id']))
                elif attr=='min_inst_id':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['min_inst_id']))
                elif attr=='min_dbg_id':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['min_dbg_id']))
                elif attr=='max_wave_lifetime':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['max_wave_lifetime']))
                elif attr=='min_wave_lifetime':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['min_wave_lifetime']))
                elif attr=='avg_wave_lifetime':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['avg_wave_lifetime']))
                elif attr=='max_cycle':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['max_cycle']))
                elif attr=='min_cycle':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(rate_d['min_cycle']))
                elif attr=='hit_rate':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['hit_rate'], 4)))
                elif attr=='miss_rate':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['miss_rate'], 4)))
                elif attr=='TG_per_CU_standard_deviation':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['TG_per_CU_standard_deviation'], 4)))
                elif attr=='cp_spi_time_avg':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['cp_spi_time_avg'], 2)))
                elif attr=='TG_per_CU_avg':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['TG_per_CU_avg'], 2)))
                elif attr=='rate':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['rate'], 4)))
                elif attr=='gds_ltc':
                    rate_d = eval(algo_['measure'])(algo_, edir, desc, warmup)
                    attr_l.append(str(round(rate_d['rate'], 4)))
            elif attr!='measure' and desc==None and edir==None:
                attr_l.append(algo_[attr])
            else:
                attr_l.append('TBD')
        return ','.join(attr_l)

    def get_measure(self):
        #pdb.set_trace()
        if (self.meas['algo'] == 'sqta_cmd_tdsq_rddone').any():
            self.meas['ave_latency'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'ave_latency', x['edir'], self.desc, x['warmup']))
            self.meas['median_latency'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'median_latency', x['edir'], self.desc, x['warmup']))
            self.meas['max_latency'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_latency', x['edir'], self.desc, x['warmup']))
            self.meas['min_latency'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_latency', x['edir'], self.desc, x['warmup']))
            self.meas['max_inst_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_inst_id', x['edir'], self.desc, x['warmup']))
            self.meas['max_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_dbg_id', x['edir'], self.desc, x['warmup']))
            self.meas['median_inst_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'median_inst_id', x['edir'], self.desc, x['warmup']))
            self.meas['median_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'median_dbg_id', x['edir'], self.desc, x['warmup']))
            self.meas['min_inst_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_inst_id', x['edir'], self.desc, x['warmup']))
            self.meas['min_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_dbg_id', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'sqta_tdsq_avg').any():
            self.meas['avg_wave_lifetime'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'avg_wave_lifetime', x['edir'], self.desc, x['warmup']))
            self.meas['max_cycle'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_cycle', x['edir'], self.desc, x['warmup']))
            self.meas['min_cycle'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_cycle', x['edir'], self.desc, x['warmup']))
            self.meas['max_inst_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_inst_id', x['edir'], self.desc, x['warmup']))
            self.meas['max_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_dbg_id', x['edir'], self.desc, x['warmup']))
            self.meas['min_inst_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_inst_id', x['edir'], self.desc, x['warmup']))
            self.meas['min_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_dbg_id', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'spisq_launch_done_ave').any():
            self.meas['max_wave_lifetime'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_wave_lifetime', x['edir'], self.desc, x['warmup']))
            self.meas['min_wave_lifetime'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_wave_lifetime', x['edir'], self.desc, x['warmup']))
            self.meas['max_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'max_dbg_id', x['edir'], self.desc, x['warmup']))
            self.meas['min_dbg_id'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'min_dbg_id', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'spisq_launch_done_idv').any():
            self.meas['wave_lifetime_idv'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'rate', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'operator_performance').any():
            self.meas['effective_execution_time_cycle'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'rate', x['edir'], self.desc, x['warmup']))
        elif ('operator_cp_spi_perf_wpg' in self.meas.loc[0,'algo']):
            self.meas['TG_per_CU_avg'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'TG_per_CU_avg', x['edir'], self.desc, x['warmup']))
            self.meas['cp_spi_time_avg'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'cp_spi_time_avg', x['edir'], self.desc, x['warmup']))
            self.meas['TG_per_CU_standard_deviation'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'TG_per_CU_standard_deviation', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'pfct_tcc').any():
            self.meas['hit_rate'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'hit_rate', x['edir'], self.desc, x['warmup']))
            self.meas['miss_rate'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'miss_rate', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'sqc_latency_hit').any():
            self.meas['rate'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'rate', x['edir'], self.desc, x['warmup']))
        elif (self.meas['algo'] == 'sqc_latency_miss').any():
            self.meas['rate'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'rate', x['edir'], self.desc, x['warmup']))
        elif ((self.meas.loc[0,'algo'] == 'tcea_rd_ltc') or
              (self.meas.loc[0,'algo'] == 'tcptcr_ltc_read') or
              (self.meas.loc[0,'algo'] == 'tcptcr_ltc_write') or
              (self.meas.loc[0,'algo'] == 'op_lds_ltc') or 
              (self.meas.loc[0,'algo'] == 'tcea_rdreq_duty')):
            self.meas['ave_cycle'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'ave_cycle', x['edir'], self.desc, x['warmup']))
        else:
            self.meas['winratio'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'winratio', x['edir'], self.desc, x['warmup']))
            self.meas['reqratio'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'reqratio', x['edir'], self.desc, x['warmup']))
            self.meas['absolute_cycle'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'absolute_cycle', x['edir'], self.desc, x['warmup']))
            self.meas['absolute_req'] = self.meta.T.apply(lambda x: 
                ComputeCoreMeasure.get_meas_(x['algo'], 'absolute_req', x['edir'], self.desc, x['warmup']))
        self.meas['measure'] = self.meta.T.apply(lambda x: 
            ComputeCoreMeasure.get_meas_(x['algo'], 'measure', x['edir'], self.desc, x['warmup']))
        self.meas['unit'] = self.meta['algo'].apply(lambda x: 
            ComputeCoreMeasure.get_meas_(x, 'unit'))
        self.meas['formula'] = self.meta['algo'].apply(lambda x: 
            ComputeCoreMeasure.get_meas_(x, 'formula'))
        self.meas['channel_risk'] = self.meta.T.apply(lambda x: 
            ComputeCoreMeasure.get_meas_(x['algo'], 'channel_risk', x['edir'], self.desc, x['warmup']))
        return self.meas
        
if __name__=='__main__':
    pass

