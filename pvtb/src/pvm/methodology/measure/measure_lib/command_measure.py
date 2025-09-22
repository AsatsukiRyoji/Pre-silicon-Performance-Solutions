#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHADER MEASURE ALGORITHMS about SP, SQ, LDS and SPI
@author: Li Lizhao
"""

import os, sys
from collections import OrderedDict as OD
import pandas as pd

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir+ '../../')

from utility.measure_util import *
import utility.util as util

def cpspi_csdata(algo, edir, desc, warmup = 1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    
    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(send = None, data_type = None, cycle = {'start_cycles': start_cycles_num})

    vec = desc[algo['vec']]                                                     # vec pattern
    ptn = desc[algo['ptn']]                                                     # pattern in vec

    vfiles, field_info = field_get(edir, vec, ptn, fld)     # get all of files and all fields
    ret_d = read_vec_file(edir, vfiles, field_info)         # get all of vec_data based with all fields
    ret_d = refresh_vecdata(ret_d, fld)                     # refresh vec_data with expected fld

    #ret_d = get_fields(edir, desc[algo['vec']], desc[algo['ptn']], fld)
    
    ret_cycle = {}
    for k in ret_d.keys():
        ret_d[k] = ret_d[k][ret_d[k]['send'] == 1]
        ret_d[k] = ret_d[k][ret_d[k]['data_type'] == 0]
        ret_d[k] = ret_d[k].astype(int)
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    
    rate_d = util.get_rate(ret_cycle, algo_algo)

    wpg = int(re.search(r'.*perf.*wpg(\d+).*', edir).group(1))      # get the wave per threadgroup from the testname

    rate_d['rate'] = round(rate_d['rate'] / 4 * wpg * desc['threads/wave'])     # per tg own 4 requests     
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    
    return rate_d

if __name__=='__main__':
    edir = '/project/bowen/a0/arch/guojiamin/gc_tree/gc/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/run/block/perf/perf_sp_ds_read_m32x32_b8_ipw64_wpg4/'
    desc = util.get_desc('bowen_ip', 'measure')
    algo = measure_algo_d['ldssp_read']
    lds_sp_read_interface_measure(algo, edir, desc, 1)
    pass


##--Malfunction snippets--
##        keys = list(cycles_d.keys())
##        for k,v in cycles_d.items():
##[FIXME]Due to some 'v' would be empty it's hard to execute initialization in loop 
##but without proper initialization the min/max wouldn't work properly on comparing
##            if k == keys[0]:  #Necessary initialization
##                min, max = min(v), max(v)
##                num = 0
##                all_cycles_l = []
##            if len(v) == 0:
##                continue
##            else:
##                if 'union' in type:
##                    min = min(v) if min(v)<min else min
##                    max = max(v) if max(v)>max else max
##                    num += len(v)
##                elif 'intersect' in type:
##                    all_cycles_l.append(v)
##                    min = min(v) if min(v)>min else min
##                    max = max(v) if max(v)<max else max
##                else:
##                    print( "[%s]%s is NYI" %(__file__, type))
##                    sys.exit()
##            if k == keys[-1]:
##                if 'intersect' in type:
##                    cycles_in_win = [i for i in all_cycles_l if i>=min and i<=max]
##                    num = len(cycles_in_win)
##                return num/float(max-min)
##        return 0
    
    
    
    
    

