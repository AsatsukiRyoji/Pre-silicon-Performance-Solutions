#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Performance Check Model
@author: Li Lizhao -> Guo Shihao
"""

import os, sys, pdb, argparse
import utility.util as util
import pandas as pd
from pandas import DataFrame as DF
from measure.core_performance_measure import ComputeCoreMeasure as CCM

cdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append('./')

algo_desc = '''Note: Please don\'t add space between algothims.

Measure method used to calculate the rate or bandwidth. Alternative algorithmn: 
        mui: Merge uniform and intersect bands which coincide at the same time.
        muu: Merge the uniform bands with all the time.
        mun: Merge the uniform bands by the method of normal distribution at all the time.
    spisq_launch:      Wave launch rate from spi to sq by the method of mui;
    spisq_launch_muu:  Wave launch rate from spi to sq by the method of muu;
    sqspi_done:        Wave done rate from sq to spi by the method of mui;
    sqspi_done_muu:    Wave done rate from sq to spi by the method of muu;
    spisq_launch_done_ave: Average wave life time;
    sqsp_simd_src:     Source request rate from sq to sp by the method of mui;
    sqsp_simd_src_mun: Source request rate from sq to sp by the method of mun;
    sqta_cmd:          Send command rate from sq to ta by the method of mui;
    sqta_cmd_mun:      Send command rate from aq to ta by the method of mun;
    tcptcr_req_muu:    Send request rate from tcp to tcr by the method of muu;
    tcea_rdreq_muu:    Read request return rate from tc to ea by the method of muu;
    eatc_rdret_muu:    Read request return rate from ea to tc by the method of muu;
    tcctcr_rdata:      Read data bandwidth to tcr from tcc by the method of mui;
    tcctcr_rdata_muu:  Read data bandwidth to tcr from tcc by the method of muu;
    tcctcr_rdata_mun:  Read data bandwidth to tcr from tcc by the method of mun;
    tcrtcc_wdata:      Write data bandwidth to tcc from tcr by the method of mui;
    tcrtcc_wdata_muu:  Write data bandwidth from tcr to tcc by the method of muu;
    tcrtcc_wdata_mun:  Write data bandwidth from tcr to tcc by the method of mun;
    tcptd_data:        Check data bandwidth from tcp to td by the method of mui;
    tcptd_data_muu:    Check data bandwidth from tcp to td by the method of muu;
    tcptd_data_mun:    Check data bandwidth from tcp to td by the method of mun;
    tdsp_data:         Check data bandwidth from td to sp by the method of mui;
    tdsp_data_muu:     Check data bandwidth from td to sp by the method of muu;
    tdsp_data_mun:     Check data bandwidth from td to sp by the method of mun;
    spisq_launch_done_ave: Get the wave life time with average;
    spisq_launch_done_idv: Get the wave life time with total waves;
For example: python3 quickm.py -a <algo1,algo2...> [-w [0|1]] [-p <test_output_path>] 
    '''

def option_parser(type=None):
    parser = argparse.ArgumentParser(description='%s' %algo_desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-a', '--algo', default= 'spisq_launch', dest= 'algo', help = 'Choose the corresponding algorithm according to the characteristics of the test')
    parser.add_argument('-d', '--desc', default= 'bowen_b0_ip', dest= 'desc', help = '<project(kongming/...)>_<environment(core/soc/...)> to pinpoint correct project description file')
    parser.add_argument('-w', '--warm', default= 1, dest= 'warm', help = 'Get start cycles of work, shift out warm up dispatches [0|1]')
    parser.add_argument('-p', '--path', default= './', dest= 'path', help = 'The path of the test that needs to be measured')
    parser.add_argument('--gui', default = False, action='store_true', dest= 'gui_en', help= 'GUI enable')
    parser.add_argument('--all', default = False, action='store_true', dest= 'all', help= 'Get all of the result about all test')
    options = parser.parse_args()
    return options

def quick_measure(desc, algos, warmup, path, gui_en):
    """Quickly get the measure with gui
    :algo: algorithms name, eg: tcctcr_data|tcctcr_rdata_muu and so on.
    """
    edir = path + '/'
    df_all = DF()
    for algo in algos.split(','):
        if type(algo) == str:
            try: algo_l = eval(algo)  #If it's a str([])
            except: algo_l = [algo]
        meta_df = DF({"edir":["./"], "warmup":[0], "algo":["spisq_launch"]})
        meta_df['edir'] = edir
        meta_df['warmup'] = int(warmup)
        meta_df['algo'] = ','.join(algo_l)
        test = edir.split('/')[-2]
        ccm = CCM(desc, meta_df)
        df = ccm.get_measure()
        df = df.drop(['edir', 'warmup'], axis=1)
        df_all = df_all.append(df)
    out = [DF()]
    df_all.T.apply(util.split_se_2df, args=(',', out)) 
    if gui_en:
        gui = util.PMGui()
        gui.run(out)
    return df_all

def get_all_measure(desc, algos, warmup, path, gui_en, all):
    """Iterate over all tests in out and compute the result for the sub-algorithm case
    """
    df_all_test = DF()
    for dirpath, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            dirname_all = dirpath + '/' + dirname
            try:
                df_single = quick_measure(desc, algos, warmup, dirname_all, gui_en)
                df_single['name'] = dirname
                df_single.insert(0, 'name', df_single.pop('name'))
                df_all_test = pd.concat([df_all_test, df_single], ignore_index = True)
            except:
                pass
        break
    with open(cdir + '/all_test_algo_result.csv', 'w' ) as f:
        df_all_test.to_csv(f)


if __name__=='__main__':
    opt = option_parser() 
    if opt.all:
        get_all_measure(opt.desc, opt.algo, opt.warm, opt.path, opt.gui_en, opt.all)
    else:
        quick_measure(opt.desc, opt.algo, opt.warm, opt.path, opt.gui_en)   
    pass





