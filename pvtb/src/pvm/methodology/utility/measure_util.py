#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance methodology measure specific utility
@author: Li Lizhao
"""
from utility.util import *
#from pmlog import PMLog
from pandas import DataFrame as DF
import pandas as pd
import numpy as np
import csv, os
import math

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
##NOTE:mutli-threading error. DONT use
##mlogger = PMLog(name='measure_util', path=cdir)

## Measure algorithm dictionary
## vec and ptn are name in description file which changes in different projects
# Three method algos - intersect or union(muu) or or normal(mun) are provided
measure_algo_d = {
    'cpspi_csdata'          : {
        'unit'              : "thread/cycle"
        ,'formula'          : "win(TGn)/(min(maxLAUNCHn)-max(minLAUNCHn))*wave_num*td64"
        ,'algorithm'        : "cpspi_csdata@merge_uniform_intersect"
        ,'measure'          : "cpspi_csdata"
        ,'vec'              : "cpspi_cadata_sim_vec"   
        ,'ptn'              : "cpspi_cadata_ptn"
    },'cpspi_csdata_mun'    : {
        'unit'              : "thread/cycle"
        ,'formula'          : "win(TGn)/(min(maxLAUNCHn)-max(minLAUNCHn))*wave_num*td64"
        ,'algorithm'        : "cpspi_csdata@merge_uniform_normal"
        ,'measure'          : "cpspi_csdata"
        ,'vec'              : "cpspi_cadata_sim_vec"   
        ,'ptn'              : "cpspi_cadata_ptn"
    },'cpspi_csdata_muu'    : {
        'unit'              : "thread/cycle"
        ,'formula'          : "win(TGn)/(min(maxLAUNCHn)-max(minLAUNCHn))*wave_num*td64"
        ,'algorithm'        : "cpspi_csdata@merge_uniform_union"
        ,'measure'          : "cpspi_csdata"
        ,'vec'              : "cpspi_cadata_sim_vec"   
        ,'ptn'              : "cpspi_cadata_ptn"
    },'spisq_launch'        : {
        'unit'              : "thread/cycle"
        ,'formula'          : "win(WAVEn)/(min(maxLAUNCHn)-max(minLAUNCHn))*td64"
        ,'algorithm'        : "spisq_launch@merge_uniform_intersect"
        ,'measure'          : "spisq_wave_launch"
        ,'vec'              : "spisq_cmd_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn"
    },'spisq_launch_muu'    : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(WAVEn)/(max(LAUNCHn)-min(LAUNCHn))*td64"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "spisq_wave_launch"
        ,'vec'              : "spisq_cmd_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn"
    },'spisq_launch_mun'    : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(WAVEn)/(max(LAUNCHn)-min(LAUNCHn))*td64"
        ,'algorithm'        : "spisq_launch@merge_uniform_normal"
        ,'measure'          : "spisq_wave_launch"
        ,'vec'              : "spisq_cmd_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn"
    },'spisq_sdata'          : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(min(maxRDRETn)-max(minRDRETn))"
        ,'algorithm'        : "spisq_sdata@merge_uniform_intersect"
        ,'measure'          : "spisq_sdata"
        ,'vec'              : "spisq_sdata_sim_vec"   
        ,'ptn'              : "spisq_sdata_ptn"
    },'spisp_vdata'          : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(min(maxRDRETn)-max(minRDRETn))"
        ,'algorithm'        : "spisp_vdata@merge_uniform_intersect"
        ,'measure'          : "spisp_vdata"
        ,'vec'              : "spisp_vdata_sim_vec"   
        ,'ptn'              : "spisp_vdata_ptn"
    },'sqspi_done'          : {
        'unit'              : "thread/cycle"
        ,'formula'          : "win(WAVEn)/(min(maxDONEn)-max(minDONEn))*td64"
        ,'algorithm'        : "spisq_done@merge_uniform_intersect"
        ,'measure'          : "sqspi_wave_done"
        ,'vec'              : "sqspi_msg_sim_vec"
        ,'ptn'              : "sqspi_done_ptn"
    },'sqspi_done_muu'      : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(WAVEn)/(max(DONEn)-min(DONEn))*td64"
        ,'algorithm'        : "spisq_done@merge_uniform_union"
        ,'measure'          : "sqspi_wave_done"
        ,'vec'              : "sqspi_msg_sim_vec"
        ,'ptn'              : "sqspi_done_ptn"
    },'spisq_launch_done_ave' : {
        'unit'              : "cycle"
        ,'formula'          : "done_cycle - launch_cycle"
        ##,'algorithm'        : "spisq_launch@average_cycle"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "spisq_wave_launch_done"
        ,'vec'              : "spisq_cmd_sim_vec,sqspi_msg_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn,sqspi_done_ptn"
    },'spisq_launch_done_idv' : {
        'unit'              : "cycle"
        ,'formula'          : "done_cycle - launch_cycle"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "spisq_wave_launch_done_idv"
        ,'vec'              : "spisq_cmd_sim_vec,sqspi_msg_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn,sqspi_done_ptn"
    ####},'operator_performance' : {
    ####    'unit'              : "cycle"
    ####    ,'formula'          : "effective_execution_time=first_queue_connect_cycle - last_wave_done_cycle"
    ####    ,'algorithm'        : "spisq_launch@merge_uniform_union"
    ####    ,'measure'          : "operator_perf"
    ####    ,'vec'              : "sqspi_msg_sim_vec"   
    ####    ,'ptn'              : "sqspi_done_ptn"
    },'operator_performance' : {
        'unit'              : "cycle"
        ,'formula'          : "effective_execution_time=last_wave_done_cycle - cp_spi_first_tg_cycle"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "op_perf_cp_spi_first_tg_cycle"
        ,'vec'              : "cpspi_cadata_sim_vec,sqspi_msg_sim_vec"   
        ,'ptn'              : "cpspi_cadata_ptn,sqspi_done_ptn"
    },'operator_cp_spi_perf_wpg4' : {
        'unit'              : "cycle"
        ,'formula'          : "tpc=tg/cu. cp_spi_time=nxt_tg_start - pre_tg_done"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "operator_cp_spi_perf"
        ,'vec'              : "spisq_cmd_sim_vec,sqspi_msg_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn,sqspi_done_ptn"
        ,'wpg'              : 4
    },'operator_cp_spi_perf_wpg8' : {
        'unit'              : "cycle"
        ,'formula'          : "tpc=tg/cu. cp_spi_time=nxt_tg_start - pre_tg_done"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "operator_cp_spi_perf"
        ,'vec'              : "spisq_cmd_sim_vec,sqspi_msg_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn,sqspi_done_ptn"
        ,'wpg'              : 8
    },'operator_cp_spi_perf_wpg16' : {
        'unit'              : "cycle"
        ,'formula'          : "tpc=tg/cu. cp_spi_time=nxt_tg_start - pre_tg_done"
        ,'algorithm'        : "spisq_launch@merge_uniform_union"
        ,'measure'          : "operator_cp_spi_perf"
        ,'vec'              : "spisq_cmd_sim_vec,sqspi_msg_sim_vec"   
        ,'ptn'              : "spisq_launch_ptn,sqspi_done_ptn"
        ,'wpg'              : 16
    },'tcptcr_req_tcrtcp_ret_read_ltc' : {
        'unit'              : "cycle"
        ,'formula'          : "CYCLE_tcrtcp_ret - CYCLE_tcptcr_req"
        ,'algorithm'        : "tcptcr@merge_uniform_union"
        ,'measure'          : "tcptcr_latency"
        ,'vec'              : "tcptcr_req_sim_vec,tcrtcp_ret_sim_vec"   
        ,'ptn'              : "tcptcr_req_sim_ptn,tcrtcp_ret_sim_ptn"
    },'tcptcr_ltc_read' : {
        'unit'              : "cycle"
        ,'formula'          : "CYCLE_tcrtcp_ret - CYCLE_tcptcr_req"
        ,'algorithm'        : "tcptcr@average"
        ,'measure'          : "tcptcr_latency_read"
        ,'vec'              : "tcptcr_req_sim_vec,tcrtcp_ret_sim_vec"   
        ,'ptn'              : "tcptcr_req_sim_ptn,tcrtcp_ret_sim_ptn"
    },'tcptcr_ltc_write' : {
        'unit'              : "cycle"
        ,'formula'          : "CYCLE_tcrtcp_ret - CYCLE_tcptcr_req"
        ,'algorithm'        : "tcptcr@average"
        ,'measure'          : "tcptcr_latency_write"
        ,'vec'              : "tcptcr_req_sim_vec,tcrtcp_ret_sim_vec"   
        ,'ptn'              : "tcptcr_req_sim_ptn,tcrtcp_ret_sim_ptn"
    },'sqsp_simd_cmd'       : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/4/INTERSECT[((max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "sqsp_simd_cmd@merge_uniform_intersect"
        ,'measure'          : "sqsp_simd_cmd_interface_measure"
        ,'vec'              : "sqsp_simd_cmd_vec"
        ,'ptn'              : "sqsp_simd_cmd_ptn"
    },'sqsp_simd_cmd_mun'   : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/4/NORMAL[(max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "sqsp_simd_cmd@merge_uniform_normal"
        ,'measure'          : "sqsp_simd_cmd_interface_measure"
        ,'vec'              : "sqsp_simd_cmd_vec"
        ,'ptn'              : "sqsp_simd_cmd_ptn"
    },'sqsp_simd_src_d'     : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/4/INTERSECT[((max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "sqsp_simd_src@merge_uniform_intersect"
        ,'measure'          : "sqsp_simd_src_interface_measure"
        ,'vec'              : "sqsp_simd_src_d_vec"
        ,'ptn'              : "sqsp_simd_src_d_ptn"
    },'sqsp_simd_src_d_mun' : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/4/NORMAL[(max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "sqsp_simd_src@merge_uniform_normal"
        ,'measure'          : "sqsp_simd_src_interface_measure"
        ,'vec'              : "sqsp_simd_src_d_vec"
        ,'ptn'              : "sqsp_simd_src_d_ptn"
    },'sqsp_simd_src_c'    : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/4/INTERSECT[((max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "sqsp_simd_src@merge_uniform_intersect"
        ,'measure'          : "sqsp_simd_src_interface_measure"
        ,'vec'              : "sqsp_simd_src_c_vec"
        ,'ptn'              : "sqsp_simd_src_c_ptn"
    },'sqsp_simd_src_c_mun' : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/4/NORMAL[(max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "sqsp_simd_src@merge_uniform_normal"
        ,'measure'          : "sqsp_simd_src_interface_measure"
        ,'vec'              : "sqsp_simd_src_c_vec"
        ,'ptn'              : "sqsp_simd_src_c_ptn"
    },'spsq_done'   : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/INTERSECT[(max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "spsq_excp@merge_uniform_intersect"
        ,'measure'          : "spsq_excp_interface_measure"
        ,'vec'              : "sqsp_excp_vec"
        ,'ptn'              : "sqsp_excp_ptn"
    },'spsq_done_mun'   : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Validn)/NORMAL[(max(Validn)-min(Validn))]*td64/ipw"
        ,'algorithm'        : "spsq_excp@merge_uniform_normal"
        ,'measure'          : "spsq_excp_interface_measure"
        ,'vec'              : "sqsp_excp_vec"
        ,'ptn'              : "sqsp_excp_ptn"
    },'sqta_cmd'            : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Sendn)/4/(max(Sendn)-min(Sendn))*td64/ipw"
        ,'algorithm'        : "sqta_cmd@merge_uniform_intersect"
        ,'measure'          : "sqta_cmd_interface_measure"
        ,'vec'              : "sqta_cmd_vec"
        ,'ptn'              : "sqta_cmd_ptn"
    },'sqta_cmd_mun'        : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Sendn)/4/(max(Sendn)-min(Sendn))*td64/ipw"
        ,'algorithm'        : "sqta_cmd@merge_uniform_normal"
        ,'measure'          : "sqta_cmd_interface_measure"
        ,'vec'              : "sqta_cmd_vec"
        ,'ptn'              : "sqta_cmd_ptn"
    },'tatcp_addr'          : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Sendn)/4/(max(Sendn)-min(Sendn))*td64/ipw"
        ,'algorithm'        : "sqta_cmd@merge_uniform_intersect"
        ,'measure'          : "tatc_addr_interface_measure"
        ,'vec'              : "tatc_addr_sim_vec"
        ,'ptn'              : "tatc_addr_ptn"
    },'tatcp_addr_mun'      : {
        'unit'              : "thread/cycle"
        ,'formula'          : "sum(Sendn)/4/(max(Sendn)-min(Sendn))*td64/ipw"
        ,'algorithm'        : "sqta_cmd@merge_uniform_normal"
        ,'measure'          : "tatc_addr_interface_measure"
        ,'vec'              : "tatc_addr_sim_vec"
        ,'ptn'              : "tatc_addr_ptn"
    },'tcptcr_req_muu'      : {
        'unit'              : "Req/cycle"
        ,'formula'          : "sum(REQn)/(max(RDREQn)-min(RDREQn))"
        ,'algorithm'        : "tcptcr_req@merge_uniform_union"
        ,'measure'          : "tcptcr_interface_measure"
        ,'vec'              : "tcptcr_req_sim_vec"
        ,'ptn'              : "tcptcr_req_ptn"
    },'tcea_rdreq_muu'      : {
        'unit'              : "Req/cycle"
        ,'formula'          : "sum(NUMn)/(max(RDREQn)-min(RDREQn))"
        ,'algorithm'        : "tcea_rdreq_muu@merge_uniform_union"
        ,'measure'          : "tcea_interface_measure"
        ,'vec'              : "tcea_rdreq_sim_vec"
        ,'ptn'              : "tcea_rdreq_ptn"
    },'tcea_rdreq_duty'      : {
        'unit'              : "Percent"
        ,'formula'          : "CYCLE_effective / CYCLE_toatl"
        ,'algorithm'        : "tcea_rdreq_muu@merge_uniform_union"
        ,'measure'          : "tcea_rdreq_duty_measure"
        ,'vec'              : "tcea_rdreq_sim_vec"
        ,'ptn'              : "tcea_rdreq_ptn"
    },'eatc_rdret_muu'      : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "eatc_rdret_muu@merge_uniform_union"
        ,'measure'          : "tcea_interface_measure"
        ,'vec'              : "tcea_rdreq_sim_vec,eatc_rdret_sim_vec"
        ,'ptn'              : "tcea_rdreq_ptn,eatc_rdret_ptn"
    },'eatc_rdret_mun'      : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "eatc_rdret_mun@merge_uniform_normal"
        ,'measure'          : "tcea_interface_measure"
        ,'vec'              : "tcea_rdreq_sim_vec,eatc_rdret_sim_vec"
        ,'ptn'              : "tcea_rdreq_ptn,eatc_rdret_ptn"
    },'tcctcr_rdata'    : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(min(maxRDRETn)-max(minRDRETn))"
        ,'algorithm'        : "tcctcr_rdata@merge_uniform_intersect"
        ,'measure'          : "tcctcr_interface_measure"
        ,'vec'              : "tcctcr_rdata_sim_vec"
        ,'ptn'              : "tcctcr_rdata_ptn"
    },'tcctcr_rdata_muu'    : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tcctcr_rdata@merge_uniform_union"
        ,'measure'          : "tcctcr_interface_measure"
        ,'vec'              : "tcctcr_rdata_sim_vec"
        ,'ptn'              : "tcctcr_rdata_ptn"
    },'tcctcr_rdata_mun'    : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tcctcr_rdata@merge_uniform_normal"
        ,'measure'          : "tcctcr_interface_measure"
        ,'vec'              : "tcctcr_rdata_sim_vec"
        ,'ptn'              : "tcctcr_rdata_ptn"
    },'tcrtcc_wdata'    : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "bin(BYTEn)/(min(maxWRRETn)-max(minWRRETn))"
        ,'algorithm'        : "tcrtcc_wdata@merge_uniform_intersect"
        ,'measure'          : "tcrtcc_interface_measure"
        ,'vec'              : "tcrtcc_wdata_sim_vec"
        ,'ptn'              : "tcrtcc_wdata_ptn"
    },'tcrtcc_wdata_muu'    : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(WRRETn)-min(WRRETn))"
        ,'algorithm'        : "tcrtcc_wdata@merge_uniform_union"
        ,'measure'          : "tcrtcc_interface_measure"
        ,'vec'              : "tcrtcc_wdata_sim_vec"
        ,'ptn'              : "tcrtcc_wdata_ptn"
    },'tcrtcc_wdata_mun'    : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(WRRETn)-min(WRRETn))"
        ,'algorithm'        : "tcrtcc_wdata@merge_uniform_normal"
        ,'measure'          : "tcrtcc_interface_measure"
        ,'vec'              : "tcrtcc_wdata_sim_vec"
        ,'ptn'              : "tcrtcc_wdata_ptn"
    },'tcptd_data'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tcptd_data@merge_uniform_intersect"
        ,'measure'          : "tcptd_interface_measure"
        ,'vec'              : "tctd_data_sim_vec"
        ,'ptn'              : "tctd_vld_data"
    },'tcptd_data_muu'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tcptd_data@merge_uniform_union"
        ,'measure'          : "tcptd_interface_measure"
        ,'vec'              : "tctd_data_sim_vec"
        ,'ptn'              : "tctd_vld_data"
    },'tcptd_data_mun'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tcptd_data@merge_uniform_normal"
        ,'measure'          : "tcptd_interface_measure"
        ,'vec'              : "tctd_data_sim_vec"
        ,'ptn'              : "tctd_vld_data"
    },'tdsp_data'           : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tdsp_data@merge_uniform_intersect"
        ,'measure'          : "tdsp_interface_measure"
        ,'vec'              : "tdsp_data_sim_vec"
        ,'ptn'              : "tdsp_data_ptn"
    },'tdsp_data_muu'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tdsp_data@merge_uniform_union"
        ,'measure'          : "tdsp_interface_measure"
        ,'vec'              : "tdsp_data_sim_vec"
        ,'ptn'              : "tdsp_data_ptn"
    },'tdsp_data_mun'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "tdsp_data@merge_uniform_normal"
        ,'measure'          : "tdsp_interface_measure"
        ,'vec'              : "tdsp_data_sim_vec"
        ,'ptn'              : "tdsp_data_ptn"
    },'ldssp_read'           : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "ldssp_data@merge_uniform_intersect"
        ,'measure'          : "ldssp_interface_measure"
        ,'vec'              : "ldssp_read_sim_vec"
        ,'ptn'              : "ldssp_read_ptn"
    },'ldssp_read_muu'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "ldssp_data@merge_uniform_union"
        ,'measure'          : "ldssp_interface_measure"
        ,'vec'              : "ldssp_read_sim_vec"
        ,'ptn'              : "ldssp_read_ptn"
    },'ldssp_read_mun'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "ldssp_data@merge_uniform_normal"
        ,'measure'          : "ldssp_interface_measure"
        ,'vec'              : "ldssp_read_sim_vec"
        ,'ptn'              : "ldssp_read_ptn"
    },'splds_idx'           : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "splds_idx@merge_uniform_intersect"
        ,'measure'          : "splds_interface_measure"
        ,'vec'              : "splds_idx_sim_vec"
        ,'ptn'              : "splds_idx_ptn"
    },'splds_idx_muu'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "splds_idx@merge_uniform_union"
        ,'measure'          : "splds_interface_measure"
        ,'vec'              : "splds_idx_sim_vec"
        ,'ptn'              : "splds_idx_ptn"
    },'splds_idx_mun'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "splds_idx@merge_uniform_normal"
        ,'measure'          : "splds_interface_measure"
        ,'vec'              : "splds_idx_sim_vec"
        ,'ptn'              : "splds_idx_ptn"
    },'lds_latency_mun'     : {
        'unit'              : "cycle"
        ,'formula'          : "(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "lds_latency@merge_uniform_union"
        ,'measure'          : "sqlds_interface_measure"
        ,'vec'              : "sqlds_idx_vec,ldssq_idxdone_vec"
        ,'ptn'              : "sqlds_idx_ptn,ldssq_idxdone_ptn"
    },'op_lds_ltc'          : {
        'unit'              : "cycle"
        ,'formula'          : "CYCLE_ret - CYCLE_req"
        ,'algorithm'        : "lds_latency@merge_uniform_union"
        ,'measure'          : "op_lds_latency"
        ,'vec'              : "sqlds_idx_vec,ldssq_idxdone_vec"
        ,'ptn'              : "sqlds_idx_ptn,ldssq_idxdone_ptn"
    },'tcea_rd_ltc'          : {
        'unit'              : "cycle"
        ,'formula'          : "CYCLE_ret - CYCLE_req"
        ,'algorithm'        : "tcea_rd_latency@merge_uniform_union"
        ,'measure'          : "tcea_rd_latency"
        ,'vec'              : "tcea_rdreq_sim_vec,eatc_rdret_sim_vec"
        ,'ptn'              : "tcea_rdreq_ptn,eatc_rdret_ptn"
    },'sxgds_data_mun'       : {
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "sxgds_data@merge_uniform_normal"
        ,'measure'          : "sxgds_interface_measure"
        ,'vec'              : "sxgds_data_sim_vec"
        ,'ptn'              : "sxgds_data_ptn"
    },'gds_latency_muu'     : {
        'unit'              : "cycle"
        ,'formula'          : "(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "gds_latency@merge_uniform_union"
        ,'measure'          : "sxgds_gdstd_interface_measure"
        ,'vec'              : "sxgds_expcmd_sim_vec,gdstd_rddone_sim_vec"
        ,'ptn'              : "sxgds_expcmd_sim_ptn,gdstd_rddone_sim_ptn"
    },'sqta_cmd_tdsq_rddone': {
        'unit'              : "Req/cycle"
        ,'formula'          : "sum(NUMn)/(max(RDREQn)-min(RDREQn))"
        ,'algorithm'        : "sqta_cmd_tdsq_rddone@merge_uniform_normal"
        ,'measure'          : "sqta_tdsq_interface_measure"
        ,'vec'              : "sqta_cmd_vec,tdsq_rddone_vec"
        ,'ptn'              : "sqta_cmd_ptn,tdsq_rddone_ptn"
    },'sqta_tdsq_avg'       : {
        'unit'              : "Req/cycle"
        ,'formula'          : "sum(NUMn)/(max(RDREQn)-min(RDREQn))"
        ,'algorithm'        : "sqta_tdsq_avg@merge_uniform_normal"
        ,'measure'          : "sqta_tdsq_avg"
        ,'vec'              : "sqta_cmd_vec,tdsq_rddone_vec"
        ,'ptn'              : "sqta_cmd_ptn,tdsq_rddone_ptn"
    },'pfct_tcc'            : {
        'unit'              : "percent" 
        ,'formula'          : "sum(hit/read)"
        ,'algorithm'        : "pfct_tcc@normal"
        ,'measure'          : "pfct_tcc_bfld_interface_measure"
        ,'vec'              : "tcc_perf_vec"
    },'sqc_latency_hit'     : {
        'unit'              : "cycle"
        ,'formula'          : ""
        ,'algorithm'        : "sqc_latency_hit@merge_uniform_union"
        ,'measure'          : "sqc_interface_hit_measure"
        ,'vec'              : "sqsqc_data_req_sim_vec,sqsqc_inst_req_sim_vec,sqcsq_data_ret_sim_vec,sqcsq_inst_ret_sim_vec"
        ,'ptn'              : "sqsqc_data_req_ptn,sqsqc_inst_req_ptn,sqcsq_data_ret_ptn,sqcsq_inst_ret_ptn"
    },'sqc_latency_miss'     : {
        'unit'              : "cycle"
        ,'formula'          : ""
        ,'algorithm'        : "sqc_latency_miss@merge_uniform_union"
        ,'measure'          : "sqc_interface_miss_measure"
        ,'vec'              : "sqctc_req_sim_vec,tcsqc_ret_sim_vec"
        ,'ptn'              : "sqctc_req_ptn,tcsqc_ret_ptn"
    }
}

#User should only use the necessary keys and corresponding value format
interface_vec_filters = {'start_cycles' : None, 'valid_cid' : []}

def dbg_id_parser(dbg_id_str, details_en=False):
    """
    E.g.'in se*_spi_sq0_cmd_sim.vec, field[2] = 32'h dbg_id'
    ME[1:0],PIPE[1:0],QUEUE[2:0],SE[2:0],WAVE_TYPE[2:0],WAVE[18:0] Also check src/meta interfaces/dbg_id.ifh
    :return: is_wave<'cs'>, dbg_id<dict>
    """
    _dbg_id = '{:0>32b}'.format(int(dbg_id_str, 16))
      #-1 is the last char, :-1] will truncate the last char, [-m:-n] returns -m,-(m-1)...-(n+1)
    dbg_id = dict(zip(
        ['wave_num', 'wave_type', 'se_id', 'queue_id', 'pipe_id', 'me_id'], 
        [_dbg_id[-19:], _dbg_id[-22:-19], _dbg_id[-25:-22], _dbg_id[-28:-25], _dbg_id[-30:-28], _dbg_id[:-30]
        ]))
    dbg_id = dict((k, int(v, 2)) for k,v in dbg_id.items())
    ##[XXX]ME_ID: {0:Invalid,1:CPC,2:Scheduler}; WAVE_TYPE: {6:CS}; WAVE_NUM: accumulated wave numbers in all time
    is_wave = {7: 'cs'}.get(dbg_id['me_id']+dbg_id['wave_type'])
    if details_en:
        return is_wave, dbg_id
    else:
        return is_wave

def interface_vec_parser(intf_vec, intf_ptn, field_d, *args, **kwargs):
    """
    read field of intf_ptn from intf_vec
    intf_vec : full path vec name
    intf_ptn : match pattern
    field_d  : dict type, {'wanted field name in vec field' : [None | {'filter name' : filter value}]}
    return:
        field_info: e.g. ['valid':['0','1'] ...]
        ret_info:   e.g. [['1', '00062586'], ...]

    e.g. se0__spi_sq0_cmd_sim.vec:
        stream se0__SPI_SQ0_cmd
        class = SPI_SQ_cmd
        field[0] = 1'h valid
        ...
        endstream
    """
    fields = list(field_d.keys())
    field_info = OrderedDict()
    ret_info = []
    with open(intf_vec, 'r') as vec:
        header_done = 0
        for ln in vec.readlines():
            if header_done == 0:    # prepare field info
                if re.search(r'^endstream', ln):
                    header_done = 1
                    continue
                    # field[10] = 1'h group_size
                l = [i for i in re.split(r"\[|\]|'|\n| ", ln) if i != '']
                if l[0] == 'field':
                    field_info[l[5]] = [l[1], l[3]]
            elif re.search(r''+intf_ptn+'', ln):
                ln_item = []
                invalid = False
                l = ln.split()
                for f in fields:
                    if f == 'cycle': #cycle is not in field in vec
                        v = l[l.index('@') + 1]
                        fl = field_d[f].get('start_cycles') if field_d[f] else None
                        if fl != None and int(v) < fl:
                            invalid = True
                    elif f == 'inst_pass':              # due to pass is key word in the python, we need a branch to extract the pass field in the *sq*sp*simd*cmd*vec
                        v = l[int(field_info["pass"][0]) + 1]
                        if f == 'cid':
                            fl = field_d[f].get('valid_cid') if field_d[f] else None
                            if fl != None and int(v, 16) not in fl:
                                invalid = True
                    else:
                        v = l[int(field_info[f][0]) + 1]
                        if f == 'cid':
                            fl = field_d[f].get('valid_cid') if field_d[f] else None
                            if fl != None and int(v, 16) not in fl:
                                invalid = True

                    if invalid == True:
                        break;
                    else: ln_item.append(v)
                if invalid == False:
                    ret_info.append(ln_item)
    return field_info, ret_info

def get_start_cycles(edir, warmup=0):
    """Get start cycles of work, shift out warm up dispatches
    The 'connected' happens on packets and events(like cache_flush), user need to take 
    care this on their own. E.g. A multiple dispatch tests has 1 warmup, 32 work and 1 
    flush at the end(a cache flush goes to tc on whatever pipe/queue), so that 34 
    'connected' are grabbed
    """
    vec = 'cpc_cpf_msgme1_sim.vec'
    vecs = file_finder(edir, vec)
    ##[XXX]use 'fromkeys' to avoid unorder issue of ordered dict 
    fld = OrderedDict.fromkeys(['pipeid','queueid','message','cycle'])
    ptn = 'CPC_CPF_msgme1\s1\s\d\s\d\s\w{2}' #valid(1) pipeid queueid message @ cycles
    fld_l, info_l = interface_vec_parser(edir+vec, ptn, fld)
    cycles_l = [int(i[-1]) for i in info_l if i[2]=='00'] #connected(00)
    return cycles_l[warmup] #all dispatches before this are warmup dispatches

def field_get(edir, vec, ptn, field_d, *args, **kwargs):
    """get the location of all field in the vec
    """

    edir = edir + '/' if not edir.endswith('/') else edir
    vecs = file_finder(edir, vec)

    field_info = ['pattern',]
    example_file = vecs[0]
    
    with open(edir + example_file, 'r') as vfile:
        header_done = 0
        for i in vfile.readlines():
            if header_done == 0:
                if re.search('^endstream', i):
                    header_done = 1
                    continue
            
                if re.search('^field', i):
                    #pdb.set_trace()
                    pre_info = re.search('\[\d+\]\s\=\s\d+\'h\s(\S+)', i).group(1)
                    field_info.append(pre_info)                 
                else:
                    continue
    
    # use extend instead of append
    field_info.extend(['break', 'cycle'])

    return vecs, field_info

def field_get_all(edir, vec, ptn, field_d, *args, **kwargs):
    """get the location of all field in the vec
    """

    edir = edir + '/' if not edir.endswith('/') else edir
    vecs = file_finder(edir, vec)
    #print("vec number: {}".format(len(vecs)))

    for vec in vecs:
        field_info = ['pattern',]        
        example_file = vec
    
        with open(edir + example_file, 'r') as vfile:
            header_done = 0
            for i in vfile.readlines():
                if header_done == 0:
                    if re.search('^endstream', i):
                        header_done = 1
                        continue
                
                    if re.search('^field', i):
                        #pdb.set_trace()
                        pre_info = re.search('\[\d+\]\s\=\s\d+\'h\s(\S+)', i).group(1)
                        field_info.append(pre_info)                 
                    else:
                        continue
        
        # use extend instead of append
        field_info.extend(['break', 'cycle'])

    return vecs, field_info

def read_vec_file(edir, file_list, field_info):
    """convert all data in vec file as a DataFrame, and remove some unuseful columns
    """
    
    vec_data = {}
    for f in file_list:
        
        # read vec file in the format table
        vec_data[f] = pd.read_csv(edir + f, names = field_info, skiprows = len(field_info) + 2, sep = '\s+', low_memory = False)

        vec_data[f].drop(['pattern', 'break'], axis = 1, inplace = True)
        vec_data[f].dropna(inplace = True)

    return vec_data

def refresh_vecdata(vec_data, key_field):
    """keep some expected data in vec DataFrame
    """
    
    start_cycle = key_field['cycle']['start_cycles']

    keys_to_delete = [key for key in vec_data.keys() if len(vec_data[key]) == 0]
    for key in keys_to_delete:
        del vec_data[key]

    for f in vec_data.keys():
        # keep the key columns 
        vec_data[f] = vec_data[f][list(key_field.keys())]
        vec_data[f] = vec_data[f][vec_data[f]['cycle'] > start_cycle]
        vec_data[f] = vec_data[f].reset_index(drop = True)
        

    return vec_data

def get_fields(edir, vec, ptn, field_d, *args, **kwargs):
    '''
    :fld:  string contains all fields required
    :RETURN: dict {'vec name': DF}
    '''
    edir = edir + '/' if not edir.endswith('/') else edir
    vecs = file_finder(edir, vec)
    fields = list(field_d.keys())
    fld_d = {}
    for vec in vecs:
        fld_l, info_l = interface_vec_parser(edir+vec, ptn, field_d, *args, **kwargs)
        _df = DF(info_l, columns=fields)
        #for info in info_l: ##[XXX]Disaster solution due to too slow
        #    _df = _df.append(dict(zip(_df.columns,info)), ignore_index=True)
        fld_d[vec] = _df
    return fld_d

def get_cycles(edir, vec, ptn, fld, warmup):
    '''
    :algo: algorithm
    :RETURN: dict{'vec name' : list of cycles}
    '''
    vecs= file_finder(edir, vec)
    strobe_cycle = get_start_cycles(edir, warmup)
    fld = dict(dbg_id=None,cycle=None)
    cycles_d = {}
    for vec in vecs:
        fld_l, info_l = interface_vec_parser(edir+vec, ptn, fld)
        cycles_d[vec] = [int(i[1]) for i in info_l if dbg_id_parser(i[0])== 'cs' and int(i[1])>strobe_cycle]
    return cycles_d     

def get_rate(cycles_d, type):
    """
    :type: str
    <format[separate|merge]>_<distribution[uniform|]>(_<window[union|intersect]> if merge)
        uniform=numbers/cycles(end-begin)
    RETURN: dict
    :out_d: separate={vecN:rateN,...}; merge={rate, num, max, min}
    """
    ##-- [XXX]Some consideration about measuring algorithm --BEGIN
    #One most important design of GPGPU is LATENCY HIDING, which means that, on system 
    #performance architecture, we should consider how to let every block in compute core can 
    #concurrently work together under heavy workload. Based on this consideration, the core level 
    #measuring methods should outstand 'parallel' capacity of the system.
    #The 'intersect' provides a good view on 'parallel' capacity. In general this method can provide 
    #a better score with large enough workload than 'union'.
    #There are also some serial scenario, like CP dispatching on 1-pipe&1-queue the 'union' is the
    #only choice. 
    #For inconsecutive scenario, the separate can be used.
    ##-- --END
    valid_type = [
        'separate_uniform', 
        'merge_uniform_union', 
        'merge_uniform_intersect',
        'merge_uniform_normal'
    ]
    if type not in valid_type:
        print( "[%s]%s is NYI" %(__file__, type))
        return 0
    out_d = {}
    normal_val_l = []
    if 'separate' in type:
        for k,v in cycles_d.items():
            if len(v) == 0:
                out_d[k] = 0   #No valid transaction
            else:
                if 'uniform' in type:
                    out_d[k] = len(v)/float(max(v)-min(v))
    elif 'merge' in type:
        val_l = list(cycles_d.values())
        num_l = [len(i) for i in val_l if len(i)>0]
        if len(num_l) == 0:
            return {}, 'No valid numbers at all'
        if 'intersect' in type and len(num_l) == 1:
            mlogger.warning("only one avaiable vec makes 'intersect' become 'union'")
        min_l = [min(i) for i in val_l if len(i)!=0]
        max_l = [max(i) for i in val_l if len(i)!=0]
        if 'union' in type:
            out_d['min'] = min(min_l)
            out_d['max'] = max(max_l)
            out_d['num'] = sum(num_l)
            ## 
            out_d['winratio'] = (max(max_l)-min(min_l))/(max(max_l)-min(min_l))
            out_d['reqratio'] = 1.0
            out_d['absolute_cycle'] = (max(max_l)-min(min_l))
            out_d['absolute_req'] = (out_d['num'])
        elif 'intersect' in type:
            out_d['min'] = max(min_l)
            out_d['max'] = min(max_l)
            out_d['num'] = len([i for v in val_l for i in v if i>out_d['min'] and i<out_d['max']])
            ##
            out_d['winratio'] = (min(max_l)-max(min_l))/(max(max_l)-min(min_l))
            out_d['reqratio'] = len([i for v in val_l for i in v if i>out_d['min'] and i<out_d['max']])/sum(num_l)
            out_d['absolute_cycle'] = (min(max_l)-max(min_l))
            out_d['absolute_req'] = out_d['num'] 
        ##The following algorithms are normally distributed
        elif 'normal' in type:
            for i in val_l:
                normal_val_l.extend(i)
            mean_cycle = np.mean(normal_val_l)
            std_cycle = np.std(normal_val_l, ddof=1)
            left_cycle = round(mean_cycle - 1.65 * std_cycle, 2)
            right_cycle = round(mean_cycle + 1.65 * std_cycle, 2)
            filter_normal_val_l = [i for i in normal_val_l if i > left_cycle and i < right_cycle]
            out_d['min'] = min(filter_normal_val_l)
            out_d['max'] = max(filter_normal_val_l)
            out_d['num'] = len(filter_normal_val_l)
            ##
            out_d['winratio'] = (max(filter_normal_val_l)-min(filter_normal_val_l))/(max(max_l)-min(min_l))
            out_d['reqratio'] = round(len(filter_normal_val_l)/len(normal_val_l), 3)
            out_d['absolute_cycle'] = (max(filter_normal_val_l)-min(filter_normal_val_l))
            out_d['absolute_req'] = out_d['num']
        if 'uniform' in type:
            out_d['rate'] = out_d['num']/float(out_d['max']-out_d['min'])
    return out_d

def get_channel_req_ratio(vecs, ret_d, rate_d, edir, min_req_ratio, max_req_ratio):
    channel_req_ratio_dict = {}
    req_throughput_l = []
    req_throughput_int_l = []
    risk_l = []
    for i in vecs:
        risk = 0
        vec_cycle_num = len(ret_d[i]['cycle'])
        req_num = len([x for x in ret_d[i]['cycle'].astype(int) if rate_d['min'] <= x <= rate_d['max']])
        ave_num = round(rate_d['num']/len(vecs),2)
        req_ave_vecs_ratio = round(req_num/float(ave_num),2)

        if (vec_cycle_num != 0)and(req_num != 0):
            req_this_vec_ratio = round(req_num/float(vec_cycle_num),2)
        else:
            req_this_vec_ratio = 0

        if not min_req_ratio < req_ave_vecs_ratio < max_req_ratio:
            risk = 1
            risk_l.append(risk)
            print("error data: %s, req_num_in_this_vec/ave_req_num= %f. is not in[%f:%f] " % (i,req_ave_vecs_ratio,min_req_ratio,max_req_ratio))

        req_throughput = round(rate_d['rate']*req_num/rate_d['num'],2)
        req_throughput_l.append(req_throughput)
        channel_req_ratio_dict[i] = [req_num,vec_cycle_num,ave_num,req_ave_vecs_ratio,req_this_vec_ratio,req_throughput]
    
    if sum(risk_l) > 0:
        channel_risk = True
    else:
        channel_risk = False

    csv_path = edir + 'channel_req_ratio.csv'
    ##os.makedirs(os.path.dirname(csv_path), exist_ok=True)                                  ##check file exist,if not,newly build.
    
    column_name = ['vec','req_num','vec_cycle_num','ave_num','req_ave_vecs_ratio','req_this_vec_ratio','req_throughput_Byte']   ##define columns name.

    '''
    df = DF(channel_req_ratio_dict)
    df.T.to_csv(csv_path, sep='\t', index=True)
    ''' 

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_name, delimiter='\t')           
        writer.writeheader()                                                               ##write column name.

        for key, values in channel_req_ratio_dict.items():
            row_dict = {'vec':key,
                        'req_num':values[0],
                        'vec_cycle_num':values[1],
                        'ave_num':values[2],
                        'req_ave_vecs_ratio':values[3],
                        'req_this_vec_ratio':values[4],
                        'req_throughput_Byte':values[5]}
            writer.writerow(row_dict)
    
    print("channel_req_ratio.csv already exits under %s" % edir)

    return channel_risk

def hex_to_decimal(hex_str):
    hex_str = hex_str.lstrip('0x')
    return int(hex_str, 16)

def calculate_standard_deviation(data_list):
    if len(data_list) == 0:
        return float('nan')
    mean = sum(data_list)/len(data_list)
    variance_sum = sum((x - mean)**2 for x in data_list)
    variance = float(variance_sum) / (len(data_list)-1)
    standard_deviation = math.sqrt(variance)
    print('[standard_deviation] is : %f' % standard_deviation)
    return standard_deviation

def cal_list_median(list):
    sorted_list = sorted(list)
    n = len(list)
    if n % 2 ==1:
        median = sorted_list[n//2]
    else:
        median = (sorted_list[n//2] + sorted_list[n//2 - 1]) / 2
    return int(median)

if __name__ == '__main__':
    #interface_vec_parser(intf_vec, intf_ptn, field, *filters, **kwargs):
    intf_vec = 'tc9_ea9_rdreq_sim.vec'
    intf_ptn = 'TC\d*_EA\d*_rdreq 1 0 \w+ 1 \d+ [\w ]+ @ \d*'
    field = {'io': None, 'size': None, 'cid': {'valid_cid': [8]}, 'tag': None, 'cycle': {'start_cycles': '00031909'}}
    #interface_vec_parser(intf_vec, intf_ptn, field)
    #get_fields('./', intf_vec, intf_ptn, field)
    get_start_cycles('./', 0)
    pass

