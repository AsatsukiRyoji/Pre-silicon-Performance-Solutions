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

def spisq_sdata(algo, edir, desc, warmup = 1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    
    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {'start_cycles': start_cycles_num})

    ret_d = get_fields(edir, desc[algo['vec']], desc[algo['ptn']], fld)
   
    ret_cycle = {}                                          # for channel_risk. keep ret_d df.keep ret_cycle dict.
    for k in ret_d.keys():
        ret_d[k] = ret_d[k].loc[ret_d[k].valid.isin(["1"])]
        ret_d[k] = ret_d[k].astype(int)
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    
    rate_d = util.get_rate(ret_cycle, algo_algo)
    rate_d['rate'] = round(rate_d['rate'] * desc['spi_sdata_data_bw'])              # Unit is Byte per cycle, and only keep the integer part

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

def spisp_vdata(algo, edir, desc, warmup = 1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    
    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {'start_cycles': start_cycles_num})

    ret_d = get_fields(edir, desc[algo['vec']], desc[algo['ptn']], fld)

    ret_cycle = {}
    for k in ret_d.keys():
        ret_d[k] = ret_d[k].loc[ret_d[k].valid.isin(["1"])]
        ret_d[k] = ret_d[k].astype(int)
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    
    rate_d = util.get_rate(ret_cycle, algo_algo)
    rate_d['rate'] = round(rate_d['rate'] * desc['spi_vdata_data_bw'])              # Unit is Byte per cycle, and only keep the integer part

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

def spisq_wave_launch(algo, edir, desc, warmup = 1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    
    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {'start_cycles': start_cycles_num})

    ret_d = get_fields(edir, desc[algo['vec']], desc[algo['ptn']], fld)
    
    ret_cycle = {}
    for k in ret_d.keys():
        ret_d_length                        = len(ret_d[k]["cycle"])
        ret_d[k]                            = ret_d[k].astype(int)
        ret_cycle[k]                            = ret_d[k]["cycle"].values.tolist()
        ret_cycle[k][-1]                        = ret_cycle[k][-4] + 16         # 16cycle to issue 4 waves
    
    rate_d = get_rate(ret_cycle, algo_algo)
    rate_d["rate"] = round(rate_d["rate"] * desc['threads/wave'], 1)    # use thread/cycle, instead of wave/cycle

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d

def sqspi_wave_done(algo, edir, desc, warmup = 1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    
    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {'start_cycles': start_cycles_num})

    ret_d = get_fields(edir, desc[algo['vec']], desc[algo['ptn']], fld)
    
    ret_cycle = {}
    for k in ret_d.keys():
        ret_d[k] = ret_d[k].astype(int)
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    
    rate_d = get_rate(ret_cycle, algo_algo)
    rate_d["rate"] = rate_d["rate"] * desc['threads/wave']             # use thread/cycle, instead of wave/cycle
    
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d


## The following function calculates the wave_rate at which SPI launch first wave to SQ to complete the last wave
def spisq_wave_launch_done(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(dbg_id = None, cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld)
    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld)
    launch_merge_df = DF()
    done_merge_df = DF()
    launch_dict = {}
    done_dict = {}
    rate_d = {}

    # merge launch df and rename cycle to launch_cycle
    for k in launch_d.keys():
        ##dict for chn_risk.
        launch_d[k]["cycle"] = launch_d[k]["cycle"].astype(int)
        launch_dict[k] = launch_d[k]["cycle"].values.tolist()
        launch_merge_df = pd.concat((launch_merge_df, launch_d[k]))
    launch_merge_df["launch_cycle"] = launch_merge_df["cycle"].astype(int)
    launch_merge_df.drop('cycle', axis=1, inplace = True)
    # merge done df and rename cycle to done_cycle
    for k1 in done_d.keys():
        ##dict for chn_risk.
        done_d[k1]["cycle"] = done_d[k1]["cycle"].astype(int)
        done_dict[k1] = done_d[k1]["cycle"].values.tolist()
        done_merge_df = pd.concat((done_merge_df, done_d[k1]))
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    # merge launch_df and done_df and the same dbg_id will automatically merged together
    total_launch_done_df = pd.merge(launch_merge_df, done_merge_df, how='outer')
    
    total_launch_done_df['wave_lifetime'] = total_launch_done_df['done_cycle'] -  total_launch_done_df['launch_cycle']

    ave_wave_lifetime = round(total_launch_done_df['wave_lifetime'].mean(),2)
    max_wave_lifetime = total_launch_done_df['wave_lifetime'].max()
    min_wave_lifetime = total_launch_done_df['wave_lifetime'].min()

    max_index = total_launch_done_df[total_launch_done_df['wave_lifetime']==max_wave_lifetime].index.min()
    min_index = total_launch_done_df[total_launch_done_df['wave_lifetime']==min_wave_lifetime].index.min()

    max_dbg_id = total_launch_done_df.loc[max_index,'dbg_id']
    min_dbg_id = total_launch_done_df.loc[min_index,'dbg_id']

    max_launch_cycle = total_launch_done_df.loc[max_index,'launch_cycle']
    min_launch_cycle = total_launch_done_df.loc[min_index,'launch_cycle']
    max_done_cycle = total_launch_done_df.loc[max_index,'done_cycle']
    min_done_cycle = total_launch_done_df.loc[min_index,'done_cycle']

    rate_d = {'max_wave_lifetime':max_wave_lifetime, 
              'min_wave_lifetime':min_wave_lifetime, 
              'ave_wave_lifetime':ave_wave_lifetime, 
              'max_dbg_id':max_dbg_id, 
              'min_dbg_id':min_dbg_id,
              'ave_cycle':ave_wave_lifetime,
              'rate':ave_wave_lifetime}

    rate_launch_d = util.get_rate(launch_dict, algo_algo) ##TODO:algo_algo?
    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_1 = util.get_channel_req_ratio(launch_d.keys(), launch_d, rate_launch_d, edir, 0.8, 1.2)
    risk_2 = util.get_channel_req_ratio(done_d.keys(), done_d, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] =(risk_1 or risk_2) ##True or False.

    return rate_d

def spisq_wave_launch_done_idv(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(dbg_id = None, cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld)
    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld)
    launch_merge_df = DF()
    done_merge_df = DF()
    launch_dict = {}
    done_dict = {}
    rate_d = {}

    # merge launch df and rename cycle to launch_cycle
    for k in launch_d.keys():
        ##dict for chn_risk.
        launch_d[k]["cycle"] = launch_d[k]["cycle"].astype(int)
        launch_dict[k] = launch_d[k]["cycle"].values.tolist()
        launch_merge_df = pd.concat((launch_merge_df, launch_d[k]))
    launch_merge_df["launch_cycle"] = launch_merge_df["cycle"].astype(int)
    launch_merge_df.drop('cycle', axis=1, inplace = True)
    # merge done df and rename cycle to done_cycle
    for k1 in done_d.keys():
        ##dict for chn_risk.
        done_d[k1]["cycle"] = done_d[k1]["cycle"].astype(int)
        done_dict[k1] = done_d[k1]["cycle"].values.tolist()
        done_merge_df = pd.concat((done_merge_df, done_d[k1]))
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    # merge launch_df and done_df and the same dbg_id will automatically merged together
   
    done_cycle = done_merge_df["done_cycle"].max()
    launch_cycle = launch_merge_df["launch_cycle"].min()

    idv_wave_lifetime = done_cycle - launch_cycle

    ##rate_d["rate"] = idv_wave_lifetime
    ##"global name 'rate_d' is not defined"

    ##rate_d = {'rate':idv_wave_lifetime}
    rate_d['rate'] = idv_wave_lifetime

    rate_launch_d = util.get_rate(launch_dict, algo_algo)
    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_1 = util.get_channel_req_ratio(launch_d.keys(), launch_d, rate_launch_d, edir, 0.8, 1.2)
    risk_2 = util.get_channel_req_ratio(done_d.keys(), done_d, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] =(risk_1 or risk_2) ##True or False.

    return rate_d


def operator_perf(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')

    f = edir + 'cpc_cpf_msgme1_sim.vec.gz'
    if os.path.exists(f):
        print( "gunzip file %s" %(f))
        os.system('gunzip -f '+ f)
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(dbg_id = None, cycle = {'start_cycles':start_cycles_num})
    
    done_vec = algo['vec']
    done_ptn = algo['ptn']
    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld)
    done_merge_df = DF()
    done_dict = {}
    rate_d = {}

    for k1 in done_d.keys():
        ##dict for chn_risk.
        done_d[k1]["cycle"] = done_d[k1]["cycle"].astype(int)
        done_dict[k1] = done_d[k1]["cycle"].values.tolist()
        done_merge_df = pd.concat((done_merge_df, done_d[k1]))
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    # merge launch_df and done_df and the same dbg_id will automatically merged together
   
    done_cycle = done_merge_df["done_cycle"].max()
    first_queue_connect_time = get_start_cycles(edir, warmup)

    effective_execution_time_cycle = done_cycle - first_queue_connect_time

    rate_d['rate'] = effective_execution_time_cycle

    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_2 = util.get_channel_req_ratio(done_d.keys(), done_d, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] = risk_2 ##True or False.

    return rate_d

def op_perf_cp_spi_first_tg_cycle(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')

    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    fld = dict(dbg_id = None, cycle = {'start_cycles':start_cycles_num})
    fld_start = dict(send = None, data_type = None, cycle = {'start_cycles':0})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    launch_vec = desc[launch_vec]
    launch_ptn = desc[launch_ptn]

    vfiles, field_info = field_get(edir, launch_vec, launch_ptn, fld_start)  # get all of files and all fields
    launch_d = read_vec_file(edir, vfiles, field_info)                       # get all of vec_data based with all fields
    launch_d = refresh_vecdata(launch_d, fld_start)                          # refresh vec_data with expected fld
    
    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld)
    done_merge_df = DF()
    done_dict = {}
    rate_d = {}

    cycle_l = []
    ret_cycle = {}
    for k in launch_d.keys():
        launch_d[k] = launch_d[k][launch_d[k]['send'] == 1]
        launch_d[k] = launch_d[k][launch_d[k]['data_type'] == 0]
        launch_d[k] = launch_d[k].astype(int)
        cycle_l.append(launch_d[k]['cycle'].reset_index(drop=True).loc[0])
        ret_cycle[k] = launch_d[k]["cycle"].values.tolist()
    cp_spi_first_tg_cycle = min(cycle_l)

    for k1 in done_d.keys():
        ##dict for chn_risk.
        done_d[k1]["cycle"] = done_d[k1]["cycle"].astype(int)
        done_dict[k1] = done_d[k1]["cycle"].values.tolist()
        done_merge_df = pd.concat((done_merge_df, done_d[k1]))
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    # merge launch_df and done_df and the same dbg_id will automatically merged together
   
    done_cycle = done_merge_df["done_cycle"].max()
    
    effective_execution_time_cycle = done_cycle - cp_spi_first_tg_cycle

    rate_d['rate'] = effective_execution_time_cycle

    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_2 = util.get_channel_req_ratio(done_d.keys(), done_d, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] = risk_2 ##True or False.

    return rate_d

def operator_cp_spi_perf(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')

    f = edir + 'cpc_cpf_msgme1_sim.vec.gz'
    if os.path.exists(f):
        print( "gunzip file %s" %(f))
        os.system('gunzip -f '+ f)
    
    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    ##fld = dict(dbg_id = None, cycle = {'start_cycles':start_cycles_num})
    fld = dict(dbg_id = None, msg = None, cycle = {'start_cycles':start_cycles_num})
    launch_fld = dict(dbg_id = None, cu_id = None, msg = None, cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], launch_fld)
    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld)
    done_merge_df = DF()
    done_dict = {}
    launch_merge_df = DF()
    launch_dict = {}
    rate_d = {}

    ##########
    results_l = {}
    tg_num_per_cu_l = []
    tg_num_per_cu_bak_l = [None]*72
    tpc_72cu_l = []  ##tpc: tg per cu.
    wpg = algo['wpg']
    
    l_columns = ['msg','cu_id','dbg_id','cycle']
    l_dfs = [pd.DataFrame(columns=l_columns) for _ in range(72)]     ## init 72 empty l_df for 72 CUs.
    l_tg_first_w_dfs = [pd.DataFrame(columns=l_columns) for _ in range(72)]
    l_tg_last_w_dfs = [pd.DataFrame(columns=l_columns) for _ in range(72)]
    l_tg_first_w_id_lists = [] 
    l_tg_first_w_cycle_lists = []
    for _ in range(72):
        l_tg_first_w_id_lists.append([])
        l_tg_first_w_cycle_lists.append([])

    for key,small_dict in launch_d.items():
        pattern = r'se(\d)'
        matches = re.search(pattern,key)
        se = int(matches.group(1))
        l_df = small_dict                                                  ## l_df :launch
        for i in range(9):
            cu = se*9 + i
            l_dfs[cu] = l_df[l_df['cu_id'].astype(int) == i]                ## l_dfs[i]: same cu_id, cu_id=i 
            l_dfs[cu]['cu_id'] = cu
            ## get each first wave_id in each tg. wave_ids are continuous in tg.
            l_tg_first_w_dfs[cu] = l_dfs[cu][l_dfs[cu]['dbg_id'].apply(util.hex_to_decimal) % wpg == 0]
            ## xxx: last_launch_wave =! last_done_wave.
            l_tg_last_w_dfs[cu] = l_dfs[cu][l_dfs[cu]['dbg_id'].apply(util.hex_to_decimal) % wpg == (wpg-1)]
            
            ##error order.
            ##tg_num_per_cu_l.append(l_dfs[cu].shape[0]/wpg)
            ##tg_num_per_cu_bak_l.insert(cu,l_dfs[cu].shape[0]/wpg)
            tg_num_per_cu_bak_l[cu] = l_dfs[cu].shape[0]/wpg
            tg_num_per_cu_l = tg_num_per_cu_bak_l 

        results_l[key] = (l_dfs, tg_num_per_cu_l)

    ##tg_num_per_cu_bak_l.clear()

    avg_tpc = sum(tg_num_per_cu_l)/len(tg_num_per_cu_l)
    print('used CU num: %d' %len(tg_num_per_cu_l))
    print('The number of TGs assigned to each CU:')
    print(tg_num_per_cu_l)

    for k1 in done_d.keys():
        ##dict for chn_risk.
        done_d[k1]["cycle"] = done_d[k1]["cycle"].astype(int)
        done_dict[k1] = done_d[k1]["cycle"].values.tolist()
        done_merge_df = pd.concat((done_merge_df, done_d[k1]))
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)

    speed_l = []
    total_last_to_first_l = []
    done_cycle_l = []
    launch_cycle_l = []
    pre_done_l = []
    next_launch_l = []
    last_wave_id_l = []

    cp_spi_launch_speed_on_cu = [[] for _ in range(72)]
    ##pre_wave_id_in_2rd_tg_to_last_tg
    ##last_wave_id_in_1st_tg_to_last_tg
    speed_dict = {}
    
    file_path = edir + 'cp_spi_launch_speed.log'

    if avg_tpc > 1:
        standard_deviation = util.calculate_standard_deviation(tg_num_per_cu_l)

    ## clear 
    with open(file_path, 'w', newline='') as file:
        file.write('[The_number_of_TGs_dispatched_to_each_CU]: %s \n' % ", ".join(map(str,tg_num_per_cu_l)))
        file.write('\n')
        file.write('[The_average_number_of_TGs_dispatched_to_each_CU]: %f \n' % avg_tpc)
        file.write('\n')
        file.write('[TG_per_CU_standard_deviation]: %f \n' % standard_deviation)
        file.write('\n')
        file.write('---Average/MAX/MIN cp_spi_launch_time are in the end of this file.--- \n')
        file.write('\n')
        file.write('cp_spi_launch_time: \n')
        file.write('\n')

    for i in range(72):
        cp_spi_launch_speed_on_cu[i].clear()
        l_tg_first_w_dfs[i] = l_tg_first_w_dfs[i].reset_index(drop=True)
        l_tg_first_w_cycle_lists[i]=l_tg_first_w_dfs[i]['cycle'].tolist()
        l_tg_first_w_id_lists[i]=l_tg_first_w_dfs[i]['dbg_id'].tolist()
        if tg_num_per_cu_l[i] > 1:  ## tg/cu=2 > 1 ?
            for k in range(1,int(tg_num_per_cu_l[i])):
                pre_launch_wave_id = util.hex_to_decimal(l_tg_first_w_id_lists[i][k-1])
                for j in range(pre_launch_wave_id,pre_launch_wave_id+wpg):
                    done_cycle_l.append(int(done_merge_df[done_merge_df['dbg_id']==(hex(j)[2:])]['done_cycle']))
                pre_done_cycle = max(done_cycle_l)
                pre_done_l.append(pre_done_cycle)
                done_cycle_l.clear()
                a_df = done_merge_df[done_merge_df['done_cycle']==(pre_done_cycle)]['dbg_id']
                last_wave_id_l.append(a_df.tolist()[0])
                
                
                next_launch_wave_id = util.hex_to_decimal(l_tg_first_w_id_lists[i][k])
                for m in range(next_launch_wave_id,next_launch_wave_id+wpg):
                    launch_cycle_l.append(int(l_dfs[i][l_dfs[i]['dbg_id']==(hex(m)[2:])]['cycle']))
                next_launch_first_cycle = min(launch_cycle_l)
                launch_cycle_l.clear()
                next_launch_l.append(next_launch_first_cycle)

                speed = next_launch_first_cycle - pre_done_cycle
                cp_spi_launch_speed_on_cu[i].append(speed)
            ##inner_dict['first_wave_id_in_next_tg'] = l_tg_first_w_id_lists[i]

            with open(file_path, 'a', newline='') as file:
                file.write('[CU_num]: %d \n' % i)
                file.write('[TGs_in_this_cu]: %d \n' % tg_num_per_cu_l[i])
                file.write('[first_wave_id_in_TG]: %s \n' % ", ".join(map(str,l_tg_first_w_id_lists[i])))
                file.write('[last_wave_done_id_in_previous_TG]: %s \n' % ", ".join(map(str,last_wave_id_l)))
                file.write('[first_launch_cycle_in_next_TG]: %s \n' % ", ".join(map(str,next_launch_l)))
                file.write('[last_done_cycle_in_previous_TG]: %s \n' % ", ".join(map(str,pre_done_l)))
                file.write('[cp_spi_launch_time(unit is cycle)]:%s \n' % ", ".join(map(str,cp_spi_launch_speed_on_cu[i])))
                file.write('\n')
             
            total_last_to_first_l.extend(cp_spi_launch_speed_on_cu[i])
            print('[CU_num]: %d ' % i)
            print('[TGs in this cu]: %d' % tg_num_per_cu_l[i])
            print('[first_wave_id_in_TG]: %s ' % ", ".join(map(str,l_tg_first_w_id_lists[i])))
            print('[last_wave_done_id_in_previous_TG]: %s ' % ", ".join(map(str,last_wave_id_l)))
            print('[first_launch_cycle_in_next_TG]: %s ' % ", ".join(map(str,next_launch_l)))
            print('[last_done_cycle_in_previous_TG]: %s ' % ", ".join(map(str,pre_done_l)))
            print('[cp_spi_launch_time(unit is cycle)]: %s ' % ", ".join(map(str,cp_spi_launch_speed_on_cu[i])))
            print()
            speed_l.clear()
            pre_done_l.clear()
            next_launch_l.clear()
            last_wave_id_l.clear()
        else:
            pass

    ## when avg_tpc>1, pre_done_l and next_launch_l are not empty.
    if avg_tpc > 1:
        cp_spi_time = sum(total_last_to_first_l)/len(total_last_to_first_l)
        with open(file_path, 'a', newline='') as file:
            file.write('[Average_cp_spi_launch_time]: %d \n' % cp_spi_time)
            file.write('\n')
            file.write('[MAX_cp_spi_launch_time]: %d \n' % max(total_last_to_first_l))
            file.write('\n')
            file.write('[MIN_cp_spi_launch_time]: %d \n' % min(total_last_to_first_l))
            file.write('\n')
            file.write('[All_cp_spi_launch_time]: %s \n' % ", ".join(map(str,total_last_to_first_l)))
            file.write('\n')
        
        print('[All_cp_spi_launch_time]:')
        print(total_last_to_first_l)
        print()
        print('[Average_cp_spi_launch_time]: %d' % cp_spi_time)
        print('[MAX_cp_spi_launch_time]: %d ' % max(total_last_to_first_l))
        print('[MIN_cp_spi_launch_time]: %d ' % min(total_last_to_first_l))
        print()

        total_last_to_first_l.clear()
        rate_d['cp_spi_time_avg'] = cp_spi_time
    else:
        rate_d['cp_spi_time_avg'] = 0

    rate_d['TG_per_CU_standard_deviation'] = standard_deviation

    print('[Average_TGs_per_CU] is : %f' % avg_tpc)
    print('[TGs_per_CU_standard_deviation] is : %f' % standard_deviation)
    print()
        
    rate_d['TG_per_CU_avg'] = avg_tpc

    rate_d['rate'] = avg_tpc

    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_2 = util.get_channel_req_ratio(done_d.keys(), done_d, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] = risk_2 ##True or False.

    return rate_d


def tcptcr_latency(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    ##algo_name, algo_algo = algo['algorithm'].split('@')

    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    ##read/write:
    ##read:op=0x00,send=1&ack=0.
    ##write:op=0x20,send=1&ack=1.
    fld_req = dict(tag = None, op = 00, cycle = {'start_cycles':start_cycles_num})
    fld_ret = dict(tag = None, send = 1, ack = 0, cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    ##launch_vec = desc[launch_vec]
    ##launch_ptn = desc[launch_ptn]

    ## 
    ##done_vec = desc[done_vec]
    ##done_ptn = desc[done_ptn]

    ##launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld_req)
    ##launch_merge_df = DF()

    ##done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld_ret)
    ##done_merge_df = DF()

    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld_req)
    launch_merge_df = DF()

    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld_ret)
    done_merge_df = DF()

    st_dict = {} 
    ed_dict = {}
    mg_dict = {}

    done_dict = {}
    rate_d = {}

    cycle_l = []
    ret_cycle = {}
    st_order = {}
    ed_order = {}
    for k in launch_d.keys():
        match = re.search(r'tcp(\d+)_tcr_req_sim\.vec',k)
        if match:
            i = int(match.group(1))
            st_dict[i] = launch_d[k]
            st_dict[i]['st_cycle'] = st_dict[i]['cycle'].astype(int)
            st_dict[i].drop('cycle', axis=1, inplace = True)
            st_dict[i].reset_index(drop=True)

            for index,row in st_dict[i].iterrows():
                value = row['tag']
                if value in st_order:
                    order = st_order[value] + 1
                else:
                    order = 1
                st_order[value] = order
                hex_order = format(order, '04x')     ## '0001'
                new_tag = hex_order + row['tag']
                st_dict[i].loc[index,'new_tag'] = new_tag
                ##st_dict[i].drop('tag', axis=1, inplace = True)
                ## st_dict[33][st_dict[33]['tag']=='0080']
            st_dict[i].drop('tag', axis=1, inplace = True)
            print(i)
            st_order.clear()


    for k1 in done_d.keys():
        match111 = re.search(r'tcr_tcp(\d+)_ret_sim\.vec',k1)
        if match111:
            j = int(match111.group(1))
            ed_dict[j] = done_d[k1]
            ed_dict[j]['ed_cycle'] = ed_dict[j]['cycle'].astype(int)
            ed_dict[j].drop('cycle', axis=1, inplace = True)
            ed_dict[j].reset_index(drop=True)

            for index,row in ed_dict[j].iterrows():
                value = row['tag']
                if value in ed_order:
                    order = ed_order[value] + 1
                else:
                    order = 1
                ed_order[value] = order
                hex_order = format(order, '04x')     ## '0001'
                new_tag = hex_order + row['tag']
                ed_dict[j].loc[index,'new_tag'] = new_tag
                ##ed_dict[j].drop('tag', axis=1, inplace = True)
                ## ed_dict[33][ed_dict[33]['tag']=='0080']
            ed_dict[j].drop('tag', axis=1, inplace = True)
            print(j)
            ed_order.clear()

    for key in st_dict.keys():
        mg_dict[key] = pd.merge(st_dict[key],ed_dict[key], how='outer')
        mg_dict[key]['latency'] = mg_dict[key]['ed_cycle'] - mg_dict[key]['st_cycle']
  

    done_cycle = done_merge_df["done_cycle"].max()
    
    effective_execution_time_cycle = done_cycle - cp_spi_first_tg_cycle

    rate_d['rate'] = effective_execution_time_cycle

    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_2 = util.get_channel_req_ratio(done_d.keys(), done_d, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] = risk_2 ##True or False.

    return rate_d


def tcptcr_latency_read(algo, edir, desc, warmup=1):

    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    ##read/write:
    ##read:op=0x00,send=1&ack=0.
    ##write:op=0x20,send=1&ack=1.
    fld_req = dict(tag = None, op = '00', cycle = {'start_cycles':start_cycles_num})
    fld_ret = dict(tag = None, send = '1', ack = '0', cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld_req)
    launch_merge_df = DF()

    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld_ret)
    done_merge_df = DF()
    
    total_df = DF()

    launch_d_key = sorted(launch_d.keys())
    done_d_key = sorted(done_d.keys())
    tcptcr_latency_list = []

    mean_ltc_per_cu_dict = {}
    median_ltc_per_cu_dict = {}

    for k in done_d_key:
        done_merge_df = done_d[k]
        done_merge_df = done_merge_df[(done_merge_df['send']=='1')&(done_merge_df['ack']=='0')]
        done_merge_df = done_merge_df.sort(columns = ['tag'])
        done_merge_df = done_merge_df.reset_index()
        ##tag ---> new_tag, encode each req&ret
        done_merge_df['tag_cnt'] = done_merge_df.groupby('tag').cumcount()
        done_merge_df['new_tag'] = done_merge_df['tag'] + '_' + done_merge_df['tag_cnt'].astype(str)
        ##
        launch_merge_df = launch_d[launch_d_key[done_d_key.index(k)]]
        launch_merge_df = launch_merge_df.sort(columns = ['tag'])
        launch_merge_df = launch_merge_df[launch_merge_df['op']=='00']
        launch_merge_df = launch_merge_df.reset_index()
        launch_merge_df['tag_cnt'] = launch_merge_df.groupby('tag').cumcount()
        launch_merge_df['new_tag'] = launch_merge_df['tag'] + '_' + launch_merge_df['tag_cnt'].astype(str)
        ##
        launch_merge_df["launch_cycle"] = launch_merge_df["cycle"].astype(int)
        done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
        launch_merge_df.drop(['index','tag','tag_cnt'], axis=1, inplace = True)
        done_merge_df.drop(['index','tag','tag_cnt'], axis=1, inplace = True)
        ##merge shared ROW on key, drop diff ROW.
        mg_df = pd.merge(done_merge_df,launch_merge_df,on = 'new_tag',how='inner')
        mg_df['latency'] = mg_df['done_cycle'] - mg_df['launch_cycle']
        total_df = pd.concat((total_df,mg_df))

        match = re.search(r'tcp(\d+)',k)
        if match:
            cu_num = int(match.group(1))
        mean_ltc_per_cu_dict[cu_num] = int(mg_df['latency'].mean()) 
        median_ltc_per_cu_dict[cu_num] = int(mg_df['latency'].median())
    
    total_df = total_df.reset_index()

    print('###[ average L1-L2 latency per cu ]###')
    print('{cu_number: average_latency} :')
    print(mean_ltc_per_cu_dict)
    print('###[ median L1-L2 latency per cu ]###')
    print('{cu_number: median_latency} :')
    print(median_ltc_per_cu_dict)

    ave_column_names = ['cu_number','average_latency']
    ave_ltc_list = [(key,value) for key,value in mean_ltc_per_cu_dict.items()]
    ave_file_path = edir + 'average_L1_L2_latency.csv' 
    with open(ave_file_path, mode='w', newline='') as ave_f:
        writer = csv.writer(ave_f)
        writer.writerow(ave_column_names)
        writer.writerows(ave_ltc_list)
    print('average_L1_L2_latency has been written to: %s ' % ave_file_path)

    median_column_names = ['cu_number','median_latency']
    median_ltc_list = [(key,value) for key,value in median_ltc_per_cu_dict.items()]
    median_file_path = edir + 'median_L1_L2_latency.csv' 
    with open(median_file_path, mode='w', newline='') as m_f:
        writer = csv.writer(m_f)
        writer.writerow(median_column_names)
        writer.writerows(median_ltc_list)
    print('median_L1_L2_latency has been written to: %s ' % median_file_path)
    
    rate_d = {}
    print('[tcp_tcr_req_ret_latency]--read:')
    if 1:
        rate_d['max_cycle'] = total_df['latency'].max() 
        rate_d['min_cycle'] = total_df['latency'].min()
        rate_d['ave_cycle'] = total_df['latency'].mean()
        rate_d['median_cycle'] = total_df['latency'].median()

        max_index = total_df[total_df['latency']== total_df['latency'].max()].index.min()
        min_index = total_df[total_df['latency']== total_df['latency'].min()].index.min()

        max_new_tag = total_df.loc[max_index,'new_tag']
        min_new_tag = total_df.loc[min_index,'new_tag']

        print('median_cycle: %d' % rate_d['median_cycle'])
        print('average_cycle: %d' % rate_d['ave_cycle'])
        print('max_cycle: %d' % rate_d['max_cycle'])
        print('min_cycle: %d' % rate_d['min_cycle'])
        print('tag_cnt of max_cycle: %s' % max_new_tag)
        print('tag_cnt of min_cycle: %s' % min_new_tag)
    else:
        print('**Error: read scenario does not exit.**')
    
    return rate_d

def tcptcr_latency_read_OLD(algo, edir, desc, warmup=1):

    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    ##read/write:
    ##read:op=0x00,send=1&ack=0.
    ##write:op=0x20,send=1&ack=1.
    fld_req = dict(tag = None, op = '00', cycle = {'start_cycles':start_cycles_num})
    fld_ret = dict(tag = None, send = '1', ack = '0', cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld_req)
    launch_merge_df = DF()

    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld_ret)
    done_merge_df = DF()

    launch_d_key = sorted(launch_d.keys())
    done_d_key = sorted(done_d.keys())
    tcptcr_latency_list = []
    for k in launch_d_key:
        ##launch_d[k] = launch_d[k].sort_values(by = ['tag','cycle'])
        ##AttributeError: 'DataFrame' object has no attribute 'sort_values'
        ##print(pd.__version__) --> '0.16.2'
        ##sort_values,verson >= 0.17.0
        launch_merge_df = launch_d[k]
        launch_merge_df = launch_merge_df.sort(columns = ['tag'])
        launch_merge_df = launch_merge_df[launch_merge_df['op']=='00']
        launch_merge_df = launch_merge_df.reset_index()
        done_merge_df = done_d[done_d_key[launch_d_key.index(k)]]
        done_merge_df = done_merge_df[(done_merge_df['send']=='1')&(done_merge_df['ack']=='0')]
        done_merge_df = done_merge_df.sort(columns = ['tag'])
        done_merge_df = done_merge_df.reset_index()
        launch_merge_df["cycle"] = launch_merge_df["cycle"].astype(int)
        done_merge_df["cycle"] = done_merge_df["cycle"].astype(int)
        tcptcr_latency_list.extend(done_merge_df["cycle"] - launch_merge_df["cycle"])
    
    rate_d = {}
    print('[tcp_tcr_req_ret_latency]--read:')
    if (len(tcptcr_latency_list)>0):
        rate_d['max_cycle'] = max(tcptcr_latency_list)
        rate_d['min_cycle'] = min(tcptcr_latency_list)
        rate_d['ave_cycle'] = int(sum(tcptcr_latency_list)/len(tcptcr_latency_list))
        rate_d['median_cycle'] = util.cal_list_median(tcptcr_latency_list)
        print('median_cycle: %d' % util.cal_list_median(tcptcr_latency_list))
        print('average_cycle: %d' % int(sum(tcptcr_latency_list)/len(tcptcr_latency_list)))
        print('max_cycle: %d' % max(tcptcr_latency_list))
        print('min_cycle: %d' % min(tcptcr_latency_list))
    else:
        print('**Error: read scenario does not exit.**')
    
    return rate_d

def tcptcr_latency_write(algo, edir, desc, warmup=1):

    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    # get warm-up cycle if have, and it will be zero if no warm-up
    start_cycles_num = get_start_cycles(edir, warmup)
    ##read/write:
    ##read:op=0x00,send=1&ack=0.
    ##write:op=0x20,send=1&ack=1.
    fld_req = dict(tag = None, op = '20', cycle = {'start_cycles':start_cycles_num})
    fld_ret = dict(tag = None, send = '1', ack = '1', cycle = {'start_cycles':start_cycles_num})
    
    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    launch_d = get_fields(edir, desc[launch_vec], desc[launch_ptn], fld_req)
    launch_merge_df = DF()

    done_d = get_fields(edir, desc[done_vec], desc[done_ptn], fld_ret)
    done_merge_df = DF()

    launch_d_key = sorted(launch_d.keys())
    done_d_key = sorted(done_d.keys())
    tcptcr_latency_list = []
    for k in launch_d_key:
        ##launch_d[k] = launch_d[k].sort_values(by = ['tag','cycle'])
        ##AttributeError: 'DataFrame' object has no attribute 'sort_values'
        ##print(pd.__version__) --> '0.16.2'
        ##sort_values,verson >= 0.17.0
        launch_merge_df = launch_d[k]
        launch_merge_df = launch_merge_df[launch_merge_df['op']=='20'] 
        launch_merge_df = launch_merge_df.sort(columns = ['tag'])
        launch_merge_df = launch_merge_df.reset_index()
        done_merge_df = done_d[done_d_key[launch_d_key.index(k)]]
        done_merge_df = done_merge_df[(done_merge_df['send']=='1')&(done_merge_df['ack']=='1')]
        done_merge_df = done_merge_df.sort(columns = ['tag'])
        done_merge_df = done_merge_df.reset_index()
        launch_merge_df["cycle"] = launch_merge_df["cycle"].astype(int)
        done_merge_df["cycle"] = done_merge_df["cycle"].astype(int)
        tcptcr_latency_list.extend(done_merge_df["cycle"] - launch_merge_df["cycle"])
    
    rate_d = {}
    print('[tcp_tcr_req_ret_latency]--write:')
    if (len(tcptcr_latency_list)>0):
        rate_d['max_cycle'] = max(tcptcr_latency_list)
        rate_d['min_cycle'] = min(tcptcr_latency_list)
        rate_d['ave_cycle'] = int(sum(tcptcr_latency_list)/len(tcptcr_latency_list))
        rate_d['median_cycle'] = util.cal_list_median(tcptcr_latency_list)
        print('median_cycle: %d' % util.cal_list_median(tcptcr_latency_list))
        print('max_cycle: %d' % max(tcptcr_latency_list))
        print('min_cycle: %d' % min(tcptcr_latency_list))
        print('average_cycle: %d' % int(sum(tcptcr_latency_list)/len(tcptcr_latency_list)))
    else:
        print('**Error: write scenario does not exit.**')
    
    return rate_d


def sqsp_simd_src_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, target = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)
    ret_cycle = {}
    for k in ret_d.keys():
        #remove the value where valid is 0 to keep valid value
        ret_d[k] = ret_d[k].loc[ret_d[k].valid.isin(["1"])]
        ret_d[k] = ret_d[k].loc[ret_d[k].target.isin(["0", "1", "4", "5", "8"])]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    rate_d = util.get_rate(ret_cycle, algo_algo)
    
    if 'structure_buffer' in edir:
        dwpi = int(re.search(r'.*perf.*dwordx(\d+).*', edir).group(1))
        ipw = 32/dwpi
    else:
        ipw = int(re.search(r'.*perf.*ipw(\d+).*', edir).group(1))      # get the inst per wave from the testname in edir
    try:
        cpi = int(re.search(r'.*perf.*comp(\d+).*', edir).group(1))     # get the comp per inst from the testname in edir
    except:
        cpi = 1                                                         # for global inst, comp is fixed at 1

    rate_d["rate"] = round(rate_d["rate"] / 4 / cpi * 64 / ipw, 3)      # translate the unit to thread per cycle, 64 means thread/wave, 4 means the effective signal per inst
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

def sqsp_simd_cmd_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, inst_pass = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)

    #[TODO] for now, the calc only fit that all of SQSP execute same or same-pass inst. Need to be optimized in the future if we use kinds of inst combination
    for k in ret_d.keys():
        #remove the value where valid is 0 to keep valid value
        ret_d[k] = ret_d[k].loc[ret_d[k].valid.isin(["1"])]
        inst_pass_num = ret_d[k]["inst_pass"].max()
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_d[k] = ret_d[k]["cycle"].values.tolist()

    rate_d = util.get_rate(ret_d, algo_algo)

    if (re.match(".*\w+f(32|16)_data_forward.*", edir)):
        algo['unit'] = 'Tflops'
    elif (re.match(".*\w+(i|u)8_data_forward.*", edir)):
        algo['unit'] = 'Tops'
    elif "_fma_" in edir:
        algo['unit'] = 'Tflops'
    else:
        pass

    ipw = int(re.search(r'.*perf.*ipw(\d+).*', edir).group(1))                  # get the inst per wave from the testname in edir

    # special case for SQ-EX-DEP scenario, will be optimized in BW B
    if re.search(r'v_(mov|lshrrev|lshlrev)_b32_then_v_readlane_b32', edir):
        ipw = ipw * 2.5
    else:
        pass

    cycle_per_inst = (int(inst_pass_num) + 1) * 4                               # translate the unit to thread per cycle, 64 means thread/wave, 4 means the effective signal per pass per inst
    # Seems it is proper to only use Tflops or Tops for mmac and fma inst
    if "mmac" in edir:
        m = int((re.search('.*mmac.*_(\d+)x\d+x\d+', edir).group(1)))
        n = int((re.search('.*mmac.*\d+x(\d+)x\d+', edir).group(1)))
        k = int((re.search('.*mmac.*\d+x\d+x(\d+)', edir).group(1)))
        total_flops = 2 * m * n * k
        if (re.match(".*\d+_f(64|32)_.*", edir)):
            freq = 1.36
        else:
            freq = 1.25
        rate_d["rate"] = round(rate_d["rate"] / cycle_per_inst * 64 * total_flops * freq / 1024, 3)     # unit is Tflops or Tops
    elif "_fma_" in edir:
        total_flops = 2
        freq = 1.36
        rate_d["rate"] = round(rate_d["rate"] / cycle_per_inst * 64 * total_flops * freq / 1024, 3)     # unit is Tflops or Tops    
    else:
        rate_d["rate"] = rate_d["rate"] / cycle_per_inst * 64 / ipw                                     # unit is thread per cycle            

    return rate_d

def spsq_excp_interface_measure(algo, edir, desc, warmup = 0):

    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)                   # get the start of 2nd dispatch if warmup = 1
    fld = dict(valid = None, cycle = {"start_cycles": warmup_start_cycles})     # provide the expected field for vec
    vec = desc[algo['vec']]                                                     # vec pattern
    ptn = desc[algo['ptn']]                                                     # pattern in vec

    vfiles, field_info = field_get(edir, vec, ptn, fld)     # get all of files and all fields
    ret_d = read_vec_file(edir, vfiles, field_info)         # get all of vec_data based with all fields
    ret_d = refresh_vecdata(ret_d, fld)                     # refresh vec_data with expected fld
   
    #ret_d = util.get_fields(edir, vec, ptn, fld)

    # per request means a inst for this vec
    for k in ret_d.keys():
        #only keep the request when valid == 1
        ret_d[k] = ret_d[k][ret_d[k]['valid'] == 1]
        ret_d[k] = ret_d[k].astype(int)
        
        #transform the value of ret_d to a list which is just include cycle
        ret_d[k] = ret_d[k]["cycle"].values.tolist()

    rate_d = util.get_rate(ret_d, algo_algo)                            # the unit is inst/cycle
    ipw = int(re.search(r'.*perf.*ipw(\d+).*', edir).group(1))          # the unit is inst/wave
    
    # special case for SQ-EX-DEP scenario, will be optimized in BW B
    if re.search(r'v_(mov|lshrrev|lshlrev)_b32_then_v_readlane_b32', edir):
        ipw = ipw * 2.5
    else:
        pass
    
    rate_d["rate"] = rate_d["rate"] * 64 / ipw                          # the unit is thread/cycle

    if (re.match(".*\w+f(32|16|8)\w+_data_forward.*", edir)):
        algo['unit'] = 'Tflops'
    elif (re.match(".*\w+(i|u)8\w+_data_forward.*", edir)):
        algo['unit'] = 'Tops'
    elif "_fma_" in edir:
        algo['unit'] = 'Tflops'
    else:
        pass
    
    # below code transform unit from thread/cycle to  Tflops pr Tops
    # Seems it is proper to only use Tflops or Tops for mmac and fma inst
    if "mmac" in edir:
        m = int((re.search('.*mmac.*_(\d+)x\d+x\d+', edir).group(1)))
        n = int((re.search('.*mmac.*\d+x(\d+)x\d+', edir).group(1)))
        k = int((re.search('.*mmac.*\d+x\d+x(\d+)', edir).group(1)))
        total_flops = 2 * m * n * k
        if (re.match(".*\d+_f(64|32)_.*", edir)):
            freq = 1.36
        else:
            freq = 1.25
        flo_per_inst_thread = total_flops / 64
        rate_d["rate"] = round(rate_d["rate"] * ipw * flo_per_inst_thread * freq / 1024, 3)     # the unit is Tflops or Tops
    elif "_fma_" in edir:
        flo_per_inst_thread = 2
        freq = 1.36
        rate_d["rate"] = round(rate_d["rate"] * ipw * flo_per_inst_thread * freq / 1024, 3)     # the unit is Tflops or Tops
    else:
        rate_d["rate"] = round(rate_d["rate"], 3)

    return rate_d

def ldssp_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]

    vfiles, field_info = field_get(edir, vec, ptn, fld)     # get all of files and all fields
    ret_d = read_vec_file(edir, vfiles, field_info)         # get all of vec_data based with all fields
    ret_d = refresh_vecdata(ret_d, fld)                     # refresh vec_data with expected fld
    #ret_d = util.get_fields(edir, vec, ptn, fld)
    
    ret_cycle = {}                                          # for channel_risk. keep ret_d df. keep ret_cycle dict.
    for k in ret_d.keys():
        #only keep the request when valid == 1
        ret_d[k] = ret_d[k][ret_d[k]['valid'] == 1]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()    # for channel_risk. keep ret_d df. keep ret_cycle dict.
    
    byte_per_req    = desc['lds_sp_read_data_bw'] * desc['lds_sp_read_data_bus']
    ##rate_d          = util.get_rate(ret_d, algo_algo)
    rate_d          = util.get_rate(ret_cycle, algo_algo)   # for channel_risk. keep ret_d df. keep ret_cycle dict.
    rate_d['rate']  = rate_d['num'] / float(rate_d['max'] - rate_d['min'] + 1)      # Here it is necessary to plus 1 for cycle
    rate_d['rate']  = round(rate_d['rate'] * byte_per_req)                          # Unit is Byte per cycle, and only keep the integer part

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d

def splds_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]

    vfiles, field_info = field_get(edir, vec, ptn, fld)     # get all of files and all fields
    ret_d = read_vec_file(edir, vfiles, field_info)         # get all of vec_data based with all fields
    ret_d = refresh_vecdata(ret_d, fld)                     # refresh vec_data with expected fld
    #ret_d = util.get_fields(edir, vec, ptn, fld)

    ret_cycle = {}                                          # for channel_risk. keep ret_d df.keep ret_cycle dict.
    for k in ret_d.keys():
        #only keep the request when valid == 1
        ret_d[k] = ret_d[k][ret_d[k]['valid'] == 1]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()    # for channel_risk. keep ret_d df. keep ret_cycle dict.
    
    byte_per_req    = desc['sp_lds_idx_data_bus'] * desc['sp_lds_idx_data_bw']
    #rate_d          = util.get_rate(ret_d, algo_algo)
    rate_d          = util.get_rate(ret_cycle, algo_algo)   # for channel_risk. keep ret_d df. keep ret_cycle dict.
    rate_d['rate']  = rate_d['num'] / float(rate_d['max'] - rate_d['min'] + 1)      # Here it is necessary to plus 1 for cycle
    rate_d['rate']  = round(rate_d['rate'] * byte_per_req)                          # Unit is Byte per cycle, and only keep the integer part

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d

def sqlds_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(send = None, cycle = {"start_cycles": warmup_start_cycles})
    fld1 = dict(valid = None, cycle = {"start_cycles": warmup_start_cycles})

    ##send_vec, done_vec = desc[algo['vec'].split(',')]
    ##send_ptn, done_ptn = desc[algo['ptn'].split(',')]
    send_vec, done_vec = algo['vec'].split(',')
    send_ptn, done_ptn = algo['ptn'].split(',')
    send_df = get_fields(edir, desc[send_vec], desc[send_ptn], fld)
    done_df = get_fields(edir, desc[done_vec], desc[done_ptn], fld1)
    send_merge_df = DF()
    done_merge_df = DF()
    send_dict = {}
    done_dict = {}
    rate_d = {}

    for k in send_df.keys():
        send_merge_df = pd.concat((send_merge_df,send_df[k]))
        ##dict for chn_risk.
        send_df[k] = send_df[k].astype(int)
        send_dict[k] = send_df[k]["cycle"].values.tolist()
    send_merge_df["send_cycle"] = send_merge_df["cycle"].astype(int)
    send_merge_df.drop('cycle', axis=1, inplace = True)

    for i in done_df.keys():
        done_merge_df = pd.concat((done_merge_df,done_df[i]))
        done_df[i] = done_df[i].astype(int)
        done_dict[i] = done_df[i]["cycle"].values.tolist()
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)

    latency = done_merge_df["done_cycle"] - send_merge_df["send_cycle"]

    rate_send_d = util.get_rate(send_dict, algo_algo)
    rate_done_d = util.get_rate(done_dict, algo_algo)
    rate_d['rate']= latency.mean()
    rate_d['rate']= rate_d['rate'].astype(int)  ##latency: int.

    ## check the balance of access to different VECs.
    risk_1 = util.get_channel_req_ratio(send_df.keys(), send_df, rate_send_d, edir, 0.8, 1.2)
    risk_2 = util.get_channel_req_ratio(done_df.keys(), done_df, rate_done_d, edir, 0.8, 1.2)
    rate_d["channel_risk"] =(risk_1 or risk_2) ##True or False.

    return rate_d

def op_lds_latency(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    ##algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(send = None, opcode = None, inst_id = None, dbg_id = None, cycle = {"start_cycles": warmup_start_cycles})
    fld1 = dict(valid = None, inst_id = None, dbg_id = None, cycle = {"start_cycles": warmup_start_cycles})

    send_vec, done_vec = algo['vec'].split(',')
    send_ptn, done_ptn = algo['ptn'].split(',')
    send_df = get_fields(edir, desc[send_vec], desc[send_ptn], fld)
    done_df = get_fields(edir, desc[done_vec], desc[done_ptn], fld1)
    send_merge_df = DF()
    done_merge_df = DF()
    total_df = DF()
    rate_d = {}

    send_d_key = sorted(send_df.keys())
    done_d_key = sorted(done_df.keys())

    for k in done_d_key:
        done_merge_df = done_df[k]
        done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
        ##add new encode for one-to-one correspondence
        done_merge_df['comb_inst_dbg_id'] = done_merge_df['inst_id'] + '_' + done_merge_df['dbg_id']
        done_merge_df.drop(['cycle','inst_id','dbg_id','valid'], axis=1, inplace = True)

        send_merge_df = send_df[send_d_key[done_d_key.index(k)]]
        send_merge_df = send_merge_df[send_merge_df['opcode']=='ee']
        send_merge_df["send_cycle"] = send_merge_df["cycle"].astype(int)
        send_merge_df['comb_inst_dbg_id'] = send_merge_df['inst_id'] + '_' + send_merge_df['dbg_id']
        send_merge_df.drop(['cycle','inst_id','dbg_id','send'], axis=1, inplace = True)

        ##merge shared ROW on key, drop diff ROW.
        mg_df = pd.merge(done_merge_df,send_merge_df,on = 'comb_inst_dbg_id',how='inner')
        mg_df['latency'] = mg_df['done_cycle'] - mg_df['send_cycle']
        total_df = pd.concat((total_df,mg_df))

    total_df = total_df.reset_index()

    rate_d = {}
    print('[lds_format inst latency]:')
    if 1:
        rate_d['max_cycle'] = total_df['latency'].max() 
        rate_d['min_cycle'] = total_df['latency'].min()
        rate_d['ave_cycle'] = total_df['latency'].mean()
        rate_d['median_cycle'] = total_df['latency'].median() 
        rate_d['rate'] = rate_d['ave_cycle']

        max_index = total_df[total_df['latency']== total_df['latency'].max()].index.min()
        min_index = total_df[total_df['latency']== total_df['latency'].max()].index.min()

        max_inst_dbg_id = total_df.loc[max_index,'comb_inst_dbg_id']
        min_inst_dbg_id = total_df.loc[min_index,'comb_inst_dbg_id']

        print('median_cycle: %d' % rate_d['median_cycle'])
        print('average_cycle: %d' % rate_d['ave_cycle'])
        print('max_cycle: %d' % rate_d['max_cycle'])
        print('min_cycle: %d' % rate_d['min_cycle'])
        print('inst_id_dbg_id of max_cycle: %s' % max_inst_dbg_id)
        print('inst_id_dbg_id of min_cycle: %s' % min_inst_dbg_id)
    else:
        print('**Error: scenario does not exit.**')
    return rate_d

def sxgds_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]

    vfiles, field_info = field_get(edir, vec, ptn, fld)     # get all of files and all fiegds
    ret_d = read_vec_file(edir, vfiles, field_info)         # get all of vec_data based with all fiegds
    for f in ret_d.keys():
        ret_d[f] = ret_d[f].loc[:, ~ret_d[f].columns.duplicated()]
    ret_d = refresh_vecdata(ret_d, fld)                     # refresh vec_data with expected fld
    #ret_d = util.get_fiegds(edir, vec, ptn, fld)

    ret_cycle = {}                                          # for channel_risk. keep ret_d df.keep ret_cycle dict.
    for k in ret_d.keys():
        #only keep the request when valid == 1
        ret_d[k] = ret_d[k][ret_d[k]['valid'] == 1]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    
    byte_per_req    = desc['sx_gds_write_data_bus'] * desc['sx_gds_write_data_bw']
    rate_d          = util.get_rate(ret_cycle, algo_algo)
    rate_d['rate']  = rate_d['num'] / float(rate_d['max'] - rate_d['min'] + 1)      # Here it is necessary to plus 1 for cycle
    rate_d['rate']  = round(rate_d['rate'] * byte_per_req)                          # Unit is Byte per cycle, and only keep the integer part

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

def sxgds_gdstd_interface_measure(algo, edir, desc, warmup):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, dbg_id = None, cycle = {"start_cycles": warmup_start_cycles})
    fld1 = dict(valid = None, dbg_id = None, cycle = {"start_cycles": warmup_start_cycles})    

    send_vec, done_vec = algo['vec'].split(',')
    send_ptn, done_ptn = algo['ptn'].split(',')
    send_df = get_fields(edir, desc[send_vec], desc[send_ptn], fld)
    done_df = get_fields(edir, desc[done_vec], desc[done_ptn], fld1)
    send_merge_df = DF()
    done_merge_df = DF()
    send_dict = {}
    done_dict = {}
    rate_d = {}

    for k in sorted(send_df.keys()):
        send_merge_df = pd.concat((send_merge_df,send_df[k]))
        send_df[k]['cycle'] = send_df[k]['cycle'].astype(int)
        df = pd.DataFrame(send_df[k])
        send_df[k] = df[df['dbg_id'].shift() != df['dbg_id']]
        send_dict[k] = send_df[k]["cycle"].values.tolist()
    send_merge_df = send_merge_df[send_merge_df['dbg_id'].shift() != send_merge_df['dbg_id']].reset_index(drop = True)
    send_merge_df["send_cycle"] = send_merge_df["cycle"].astype(int)
    send_merge_df.drop('cycle', axis=1, inplace = True)

    for i in sorted(done_df.keys()):
        done_merge_df = pd.concat((done_merge_df,done_df[i]))
        done_df[i]['cycle'] = done_df[i]['cycle'].astype(int)
        done_dict[i] = done_df[i]["cycle"].values.tolist()
    done_merge_df = done_merge_df[done_merge_df['dbg_id'].shift() != done_merge_df['dbg_id']].reset_index(drop = True)
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    #with open('send_df.txt', 'w') as file: file.write(str(send_df))
    #with open('done_df.txt', 'w') as file: file.write(str(done_df))
    #with open('send_merge_df.txt', 'w') as file: file.write(str(send_merge_df))
    #with open('done_merge_df.txt', 'w') as file: file.write(str(done_merge_df))
    latency = done_merge_df["done_cycle"] - send_merge_df["send_cycle"]
    latency = latency.reset_index(drop = True).dropna()
    rate_send_d = util.get_rate(send_dict, algo_algo)
    rate_done_d = util.get_rate(done_dict, algo_algo)
    rate_d['rate']= latency.mean()
    rate_d['rate']= rate_d['rate'].astype(int)  ##latency: int.

    ## check the balance of access to different VECs.
    risk_1 = util.get_channel_req_ratio(send_df.keys(), send_df, rate_send_d, edir, 0.8, 1.2)
    risk_2 = util.get_channel_req_ratio(done_df.keys(), done_df, rate_done_d, edir, 0.8, 1.2)
    rate_d["channel_risk"] =(risk_1 or risk_2) ##True or False.

    return rate_d

def sqc_interface_hit_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld_send_data  = dict(send  = None, dbg_id = None , cycle = {"start_cycles": warmup_start_cycles})
    fld_send_inst  = dict(send  = None, dbg_id = None , cycle = {"start_cycles": warmup_start_cycles})
    fld_done_data  = dict(valid = None, dbg_id = None , cycle = {"start_cycles": warmup_start_cycles})
    fld_done_inst  = dict(valid = None, dbg_id = None , cycle = {"start_cycles": warmup_start_cycles})

    send_data_vec, send_inst_vec, done_data_vec, done_inst_vec = algo['vec'].split(',')
    send_data_ptn, send_inst_ptn, done_data_ptn, done_inst_ptn = algo['ptn'].split(',')
    print("edir:{}, warmup_start_cycles:{}".format(edir,warmup_start_cycles))
    
    send_data_vfiles, send_data_field_info = field_get_all(edir, desc[send_data_vec], desc[send_data_ptn], fld_send_data)     # get all of files and all fields
    send_inst_vfiles, send_inst_field_info = field_get_all(edir, desc[send_inst_vec], desc[send_inst_ptn], fld_send_inst)     # get all of files and all fields
    done_data_vfiles, done_data_field_info = field_get_all(edir, desc[done_data_vec], desc[done_data_ptn], fld_done_data)     # get all of files and all fields
    done_inst_vfiles, done_inst_field_info = field_get_all(edir, desc[done_inst_vec], desc[done_inst_ptn], fld_done_inst)     # get all of files and all fields
    send_data_df = read_vec_file(edir, send_data_vfiles, send_data_field_info)         # get all of vec_data based with all fields
    send_inst_df = read_vec_file(edir, send_inst_vfiles, send_inst_field_info)         # get all of vec_data based with all fields
    done_data_df = read_vec_file(edir, done_data_vfiles, done_data_field_info)         # get all of vec_data based with all fields
    done_inst_df = read_vec_file(edir, done_inst_vfiles, done_inst_field_info)         # get all of vec_data based with all fields
    send_data_df = refresh_vecdata(send_data_df, fld_send_data)                     # refresh vec_data with expected fld
    send_inst_df = refresh_vecdata(send_inst_df, fld_send_inst)                     # refresh vec_data with expected fld
    done_data_df = refresh_vecdata(done_data_df, fld_done_data)                     # refresh vec_data with expected fld
    done_inst_df = refresh_vecdata(done_inst_df, fld_done_inst)                     # refresh vec_data with expected fld

    send_data_merge_df = DF()
    send_inst_merge_df = DF()
    done_data_merge_df = DF()
    done_inst_merge_df = DF()
    rate_d = {}

    # merge df from different vecs
    for k in send_data_df.keys():
        send_data_merge_df = pd.concat((send_data_merge_df, send_data_df[k]))
    for i in send_inst_df.keys():
        send_inst_merge_df = pd.concat((send_inst_merge_df, send_inst_df[i]))
    for j in done_data_df.keys():
        done_data_merge_df = pd.concat((done_data_merge_df, done_data_df[j]))
    for l in done_inst_df.keys():
        done_inst_merge_df = pd.concat((done_inst_merge_df, done_inst_df[l]))
    #send_data_merge_df.to_csv("send_data_merge_df") 
    
    # column "cycle" rename
    send_data_merge_df.rename(columns={'cycle':'send_data_cycle'}, inplace=True)
    send_inst_merge_df.rename(columns={'cycle':'send_inst_cycle'}, inplace=True)
    done_data_merge_df.rename(columns={'cycle':'done_data_cycle'}, inplace=True)
    done_inst_merge_df.rename(columns={'cycle':'done_inst_cycle'}, inplace=True)

    # measure dcache latency
    merge_df_data = pd.merge(send_data_merge_df, done_data_merge_df, on=['dbg_id'])
    merge_df_data['d_latency'] = merge_df_data['done_data_cycle'] - merge_df_data['send_data_cycle']
    avg_d_latency = merge_df_data['d_latency'].mean()
    merge_df_data.to_csv("merge_df_data")

    # mesure icache latency
    merge_df_inst = pd.merge(send_inst_merge_df, done_inst_merge_df, on=['dbg_id'])
    merge_df_inst['i_latency'] = merge_df_inst['done_inst_cycle'] - merge_df_inst['send_inst_cycle']
    avg_i_latency = merge_df_inst['i_latency'].mean()
    merge_df_inst.to_csv("merge_df_inst")

    print("SQC-dcache average hit latency:{}".format(avg_d_latency))
    print("SQC-icache average hit latency:{}".format(avg_i_latency))

    rate_d['rate']= avg_d_latency
    return rate_d

def sqc_interface_miss_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld  = dict(send  = None, addr = None, tag = None , cycle = {"start_cycles": warmup_start_cycles})
    fld1 = dict(valid = None, tag = None , cycle = {"start_cycles": warmup_start_cycles})

    send_vec, done_vec = algo['vec'].split(',')
    send_ptn, done_ptn = algo['ptn'].split(',')
    print("send_vec:{},done_vec:{},send_ptn:{},done_ptn:{}".format(desc[send_vec],desc[done_vec],send_ptn,done_ptn))
    print("edir:{}, warmup_start_cycles:{}".format(edir,warmup_start_cycles))

    send_vfiles, send_field_info = field_get_all(edir, desc[send_vec], desc[send_ptn], fld)     # get all of files and all fields
    done_vfiles, done_field_info = field_get_all(edir, desc[done_vec], desc[done_ptn], fld1)
    send_df = read_vec_file(edir, send_vfiles, send_field_info) # get all of vec_data based with all fields
    done_df = read_vec_file(edir, done_vfiles, done_field_info) # get all of vec_data based with all fields
    send_df = refresh_vecdata(send_df, fld)                     # refresh vec_data with expected fld   
    done_df = refresh_vecdata(done_df, fld1)                    # refresh vec_data with expected fld
    done_df_filtered = {}

    send_merge_df = DF()
    done_merge_df = DF()
    send_group_df = DF()
    done_group_df = DF()
    rate_d = {}
       
    for k in send_df.keys():
        send_merge_df = pd.concat((send_merge_df,send_df[k]))
          
    for i in done_df.keys():
        # remove prev data with same tag
        if "tag" in done_df[i].columns:
            done_df[i]["prev_tag"] = done_df[i]["tag"].shift(1)
            mask = done_df[i]["tag"] == done_df[i]["prev_tag"]
            done_df_filtered[i] = done_df[i][mask]
            done_df_filtered[i] = done_df_filtered[i].drop("prev_tag",axis=1)
            done_df_filtered[i] = done_df_filtered[i].reset_index(drop=True)
        else:
            print("columns 'tag' does not exist")

        done_merge_df = pd.concat((done_merge_df, done_df_filtered[i]))

#    send_merge_df.to_csv("send_merge_df")      
    send_merge_df.rename(columns={'cycle':'send_cycle'}, inplace=True)
    send_group_df = send_merge_df.sort(['tag', 'send_cycle'],ascending=[True,True])
    send_group_df.reset_index(drop=True,inplace=True)
    send_group_df.to_csv("send_group_df")      

#    done_merge_df.to_csv("done_merge_df")
    done_merge_df.rename(columns={'cycle':'done_cycle'}, inplace=True)
    done_group_df = done_merge_df.sort(['tag', 'done_cycle'],ascending=[True,True])
    done_group_df.reset_index(drop=True,inplace=True)
    done_group_df.to_csv("done_group_df")

    merge_df = pd.concat([send_group_df[['addr','tag','send','send_cycle']], done_group_df[['valid','done_cycle']]],axis=1)
    merge_df.reset_index(drop=True,inplace=True)
    merge_df["latency"] = merge_df["done_cycle"] - merge_df["send_cycle"]
    merge_df.to_csv("merge_df")
    avg_latency = merge_df["latency"].mean()

    tag_latency = merge_df.groupby('tag')['latency'].mean().reset_index()
    addr_latency = merge_df.groupby('addr')['latency'].mean().reset_index()
    tag_latency.to_csv("tag_latency")
    addr_latency.to_csv("addr_latency")
    
    print("SQC average miss latency:{}".format(avg_latency))

    rate_d['rate']= avg_latency
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
    
    
    
    
    

