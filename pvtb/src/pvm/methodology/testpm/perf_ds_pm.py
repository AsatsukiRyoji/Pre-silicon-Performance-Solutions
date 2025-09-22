#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS read matrix (To VGPR) Performance Model
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
dv_dir = cdir + '/../../shader/'
testpm_cfg_d = {
    '_ds'       : {
        'dv'            : dv_dir + 'perf_ds.dv'
        ,'test_ptn'     : "perf_ds_(\w+)_ipw(\d+)_wpg(\d+)"
        ,'test_param_l' : ['inst_type', 'ds_inst', 'wpg']
        ,'warmup'       : 1
    }
}

class DsPM(PerfTestPM):
    def __init__(self):
        # call the __init__ func of parent class
        super(DsPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['_ds'] 

    def theory(self, desc, test = None, gui_en = False, **kw):
        """
        DS read matrix (To VGPR) Performance Model
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
        
        meta_col = ['name',
                    'wpg',                                              # for cp theory
                    'vgpr', 'unorder',                                  # for spi theory
                    'valu',                                             # for sq theory
                    'vop32',                                            # for sp theory
                    'inst_type', 'ds_inst', 'ds_PAY', 'sp_ds_PAY'       # for lds theory
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
        meta_df['valu']  = 1            # for buffer load dw, it shoud be 8 at less.
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32']    = meta_df['valu']       # for sp using, instead of sq issuing
        ##workload,unit:Byte
        ds_sp_wkld = {}
        ##ds_m* inst: vdst[4:7], vaddr.it is from ds_read_b128B, so it is 16 Byte.
        ds_sp_wkld['read_m32x16_b16_alt'] = '16'
        ds_sp_wkld['read_m32x64_b4'] = '16'
        ds_sp_wkld['read_m32x32_b8'] = '16'
        ds_sp_wkld['read_m32x16_b16'] = '16'
        ds_sp_wkld['read_m32x8_b32'] = '16'
        ds_sp_wkld['read_m64x16_b8_alt4'] = '16'
        ds_sp_wkld['read_m32x32_b8_alt2'] = '16'
        ds_sp_wkld['read_m16x16_b32'] = '16'
        ds_sp_wkld['read_mt16x16_b32'] = '16'
        ds_sp_wkld['read_mt16x32_b16_alt2'] = '16'
        ##ds_read_matrix_format (ds_s_read_m*) vdst modifiers
        ds_sp_wkld['s_read_m32x64_b4'] = '16'
        ds_sp_wkld['s_read_m32x32_b8'] = '16'
        ds_sp_wkld['s_read_m32x32_b8_alt2'] = '16'
        ds_sp_wkld['s_read_m64x16_b8_alt4'] = '16'
        ds_sp_wkld['s_read_m32x16_b16'] = '16'
        ds_sp_wkld['s_read_m32x16_b16_alt2'] = '16'
        ds_sp_wkld['s_read_m16x16_b32'] = '16'
        ds_sp_wkld['s_read_mt128x16_b4'] = '16'
        ds_sp_wkld['s_read_mt64x16_b8'] = '16'
        ds_sp_wkld['s_read_mt32x32_b8_alt2'] = '16'
        ds_sp_wkld['s_read_mt32x16_b16'] = '16'
        ds_sp_wkld['s_read_mt16x32_b16_alt2'] = '16'
        ds_sp_wkld['s_read_mt16x16_b32'] = '16'
        ##ds_write_matrix_format vdata1 modifiers
        ds_sp_wkld['s_write_m32x64_b4'] = '0'
        ds_sp_wkld['s_write_m32x32_b8'] = '0'
        ds_sp_wkld['s_write_m32x32_b8_alt2'] = '0'
        ds_sp_wkld['s_write_m64x16_b8_alt4'] = '0'
        ds_sp_wkld['s_write_m32x16_b16'] = '0'
        ds_sp_wkld['s_write_m32x16_b16_alt2'] = '0'
        ds_sp_wkld['s_write_m16x16_b32'] = '0'
        ds_sp_wkld['s_write_mt128x16_b4'] = '0'
        ds_sp_wkld['s_write_mt64x16_b8'] = '0'
        ds_sp_wkld['s_write_mt32x32_b8_alt2'] = '0'
        ds_sp_wkld['s_write_mt32x16_b16'] = '0'
        ds_sp_wkld['s_write_mt16x32_b16_alt2'] = '0'
        ds_sp_wkld['s_write_mt16x16_b32'] = '0'

        ##ds_read: vdst, vaddr
        ds_sp_wkld['read_b32'] = '4'
        ds_sp_wkld['read_i8'] = '4'
        ds_sp_wkld['read_i8_d16'] = '4'
        ds_sp_wkld['read_i8_d16_hi'] = '4'
        ##ds_inst: vdst, vaddr, vdata
        ds_sp_wkld['add_rtn_u32'] = '4'
        ds_sp_wkld['and_rtn_b32'] = '4'
        ds_sp_wkld['max_rtn_i32'] = '4'
        ds_sp_wkld['min_rtn_u32'] = '4'
        ds_sp_wkld['xor_rtn_b32'] = '4'
        ds_sp_wkld['dec_rtn_u32'] = '4'
        ds_sp_wkld['permute_b32'] = '4'
        ds_sp_wkld['bpermute_b32'] = '4'
        ds_sp_wkld['pk_add_rtn_bf16'] = '4'
        ds_sp_wkld['pk_add_rtn_f16'] = '4'
        ##ds_inst: vaddr, vdata
        ds_sp_wkld['max_u32'] = '0'
        ds_sp_wkld['min_u32'] = '0'
        ds_sp_wkld['xor_b32'] = '0'
        ds_sp_wkld['dec_u32'] = '0'
        ds_sp_wkld['add_u32'] = '0'
        ds_sp_wkld['write_b8_d16_hi'] = '0'
        ds_sp_wkld['write_b16_d16_hi'] = '0'
        ds_sp_wkld['pk_add_bf16'] = '0'
        ds_sp_wkld['pk_add_f16'] = '0'
        ds_sp_wkld['min_f32'] = '0'
        ds_sp_wkld['min_f64'] = '0'
        ds_sp_wkld['add_f32'] = '0'
        ds_sp_wkld['max_f64'] = '0'
        ##ds_inst: vdst, vaddr, vdata0, vdata1
        ds_sp_wkld['wrap_rtn_b32'] = '4'
        ds_sp_wkld['cmpst_rtn_b32'] = '4'
        ds_sp_wkld['read_mask_b32'] = '4'
        ##ds_inst: vdst, vaddr, vdata
        ds_sp_wkld['read_pack_l_b16'] = '4'
        ds_sp_wkld['read_pack_h_b16'] = '4'
        ds_sp_wkld['read_pack_0_b8'] = '4'
        ds_sp_wkld['read_pack_1_b8'] = '4'
        ds_sp_wkld['read_pack_2_b8'] = '4'
        ds_sp_wkld['read_pack_3_b8'] = '4'
        
        ##workload,unit:Byte
        sp_ds_wkld = {}
        ##ds_m* inst: vdst[4:7], vaddr.
        sp_ds_wkld['read_m32x16_b16_alt'] = '4'
        sp_ds_wkld['read_m32x64_b4'] = '4'
        sp_ds_wkld['read_m32x32_b8'] = '4'
        sp_ds_wkld['read_m32x16_b16'] = '4'
        sp_ds_wkld['read_m32x8_b32'] = '4'
        sp_ds_wkld['read_m64x16_b8_alt4'] = '4'
        sp_ds_wkld['read_m32x32_b8_alt2'] = '4'
        sp_ds_wkld['read_m16x16_b32'] = '4'
        sp_ds_wkld['read_mt16x16_b32'] = '4'
        sp_ds_wkld['read_mt16x32_b16_alt2'] = '4'
        ##ds_read_matrix_format (ds_s_read_m*) vdst modifiers
        sp_ds_wkld['s_read_m32x64_b4'] = '0'
        sp_ds_wkld['s_read_m32x32_b8'] = '0'
        sp_ds_wkld['s_read_m32x32_b8_alt2'] = '0'
        sp_ds_wkld['s_read_m64x16_b8_alt4'] = '0'
        sp_ds_wkld['s_read_m32x16_b16'] = '0'
        sp_ds_wkld['s_read_m32x16_b16_alt2'] = '0'
        sp_ds_wkld['s_read_m16x16_b32'] = '0'
        sp_ds_wkld['s_read_mt128x16_b4'] = '0'
        sp_ds_wkld['s_read_mt64x16_b8'] = '0'
        sp_ds_wkld['s_read_mt32x32_b8_alt2'] = '0'
        sp_ds_wkld['s_read_mt32x16_b16'] = '0'
        sp_ds_wkld['s_read_mt16x32_b16_alt2'] = '0'
        sp_ds_wkld['s_read_mt16x16_b32'] = '0'
        ##ds_write_matrix_format vdata1 modifiers
        sp_ds_wkld['s_write_m32x64_b4'] = '16'
        sp_ds_wkld['s_write_m32x32_b8'] = '16'
        sp_ds_wkld['s_write_m32x32_b8_alt2'] = '16'
        sp_ds_wkld['s_write_m64x16_b8_alt4'] = '16'
        sp_ds_wkld['s_write_m32x16_b16'] = '16'
        sp_ds_wkld['s_write_m32x16_b16_alt2'] = '16'
        sp_ds_wkld['s_write_m16x16_b32'] = '16'
        sp_ds_wkld['s_write_mt128x16_b4'] = '16'
        sp_ds_wkld['s_write_mt64x16_b8'] = '16'
        sp_ds_wkld['s_write_mt32x32_b8_alt2'] = '16'
        sp_ds_wkld['s_write_mt32x16_b16'] = '16'
        sp_ds_wkld['s_write_mt16x32_b16_alt2'] = '16'
        sp_ds_wkld['s_write_mt16x16_b32'] = '16'
        ##ds_read: vdst, vaddr
        sp_ds_wkld['read_b32'] = '4'
        sp_ds_wkld['read_i8'] = '4'
        sp_ds_wkld['read_i8_d16'] = '4'
        sp_ds_wkld['read_i8_d16_hi'] = '4'
        ##ds_inst: vdst, vaddr, vdata
        sp_ds_wkld['add_rtn_u32'] = '8'
        sp_ds_wkld['and_rtn_b32'] = '8'
        sp_ds_wkld['max_rtn_i32'] = '8'
        sp_ds_wkld['min_rtn_u32'] = '8'
        sp_ds_wkld['xor_rtn_b32'] = '8'
        sp_ds_wkld['dec_rtn_u32'] = '8'
        sp_ds_wkld['permute_b32'] = '8'
        sp_ds_wkld['bpermute_b32'] = '8'
        sp_ds_wkld['pk_add_rtn_bf16'] = '8'
        sp_ds_wkld['pk_add_rtn_f16'] = '8'
        ##ds_inst: vaddr, vdata
        sp_ds_wkld['max_u32'] = '8'
        sp_ds_wkld['min_u32'] = '8'
        sp_ds_wkld['xor_b32'] = '8'
        sp_ds_wkld['dec_u32'] = '8'
        sp_ds_wkld['add_u32'] = '8'
        sp_ds_wkld['write_b8_d16_hi'] = '8'
        sp_ds_wkld['write_b16_d16_hi'] = '8'
        sp_ds_wkld['pk_add_bf16'] = '8'
        sp_ds_wkld['pk_add_f16'] = '8'
        sp_ds_wkld['min_f32'] = '8'
        sp_ds_wkld['min_f64'] = '12'
        sp_ds_wkld['add_f32'] = '8'
        sp_ds_wkld['max_f64'] = '12'
        
        ##ds_inst: vdst, vaddr, vdata0, vdata1
        sp_ds_wkld['wrap_rtn_b32'] = '12'
        sp_ds_wkld['cmpst_rtn_b32'] = '12'
        sp_ds_wkld['read_mask_b32'] = '12'
        ##ds_inst: vdst, vaddr, vdata
        sp_ds_wkld['read_pack_l_b16'] = '4'
        sp_ds_wkld['read_pack_h_b16'] = '4'
        sp_ds_wkld['read_pack_0_b8'] = '4'
        sp_ds_wkld['read_pack_1_b8'] = '4'
        sp_ds_wkld['read_pack_2_b8'] = '4'
        sp_ds_wkld['read_pack_3_b8'] = '4'
        

        meta_df['ds_PAY']    = meta_df['inst_type'].replace(ds_sp_wkld)
        meta_df['ds_PAY']    = meta_df['ds_PAY'].astype(int)   ##m['ds_workload'] = m['ds_PAY']*m['ds_inst']*d['threads/wave'], m['ds_PAY'] is str,can't multi int/float, need to change type.
        meta_df['sp_ds_PAY'] = meta_df['inst_type'].replace(sp_ds_wkld)
        meta_df['sp_ds_PAY'] = meta_df['sp_ds_PAY'].astype(int)

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
    buflv = DsPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

