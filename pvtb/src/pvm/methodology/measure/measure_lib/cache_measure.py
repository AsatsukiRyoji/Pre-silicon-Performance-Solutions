#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCCEA MEASURE ALGORITHMS about TCC,EA
@author:
"""
import os, sys, re, pdb
from collections import OrderedDict as oodict
from pandas import DataFrame as DF
import pandas as pd


cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir+ '../../')

import utility.util as util
####################################################################################### 
#Notice: warmup must be zero for function tcea_interface_measure()
#The value of desc is a dictionary like  {'spisq_cmd_sim_vec': 'se\\d__spi_sq0_cmd_sim.vec', 'eatc_rdret_sim_vec': 'ea\\d+_tc\\d+_rdret_sim.vec', 'tcea_rdreq_sim_vec': 'tc\\d+_ea\\d+_rdreq_sim.vec', 'sqspi_msg_sim_vec': 'se\\d__sq0_spi_msg_sim.vec', 'sqspi_done_ptn': 'se\\d__SQ0_SPI_msg\\s1\\s00\\s', 'cp_dispatch_tg_payload': 16.0, 'eatc_rdret_ptn': 'EA\\d+_TC\\d+_rdret\\s\\d\\s\\d(\\s\\w+)+', 'bytes/addr_ds': 4.0, 'bytes/vgpr': 4.0, 'spisq_launch_ptn': 'se\\d__SPI_SQ0_cmd\\s1\\s1\\s\\w+\\s\\w+\\s0', 'threads/wave': 64.0, 'tcea_rdreq_ptn': 'TC\\d+_EA\\d+_rdreq\\s\\d\\s\\d(\\s\\w+)+', 'bytes/sgpr': 4.0}
#The value of algo is a dictonary like {'formula': 'sum(BYTEn)/(max(RDRETn)-min(RDRETn))', 'vec': 'tcea_rdreq_sim_vec,eatc_rdret_sim_vec', 'unit': 'Byte/cycle', 'measure': 'tcea_interface_measure', 'algorithm': 'eatc_rdret@merge_uniform_union', 'ptn': 'tcea_rdreq_ptn,eatc_rdret_ptn'}
#######################################################################################

############################# SQ_TA_cmd - TD_SQ_rddone latency ########################################
def sqta_tdsq_interface_measure(algo, edir, desc, warmup):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    warmup = 0
    algo_name, algo_algo = algo['algorithm'].split('@')
    start_cycles_num = util.get_start_cycles(edir, warmup)
    fld_cmd = dict(send = None, dbg_id = None, inst_id = None, cycle = {'start_cycles':start_cycles_num})       ##cmd signal 'send', cycle&id is common.
    fld_done = dict(valid = None, dbg_id = None, inst_id = None, cycle = {'start_cycles':start_cycles_num})     ##done signal 'valid', cycle&id is common.

    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    launch_df = util.get_fields(edir, desc[launch_vec], desc[launch_ptn] , fld_cmd)
    done_df = util.get_fields(edir, desc[done_vec], desc[done_ptn] , fld_done)

    launch_merge_df = DF()
    done_merge_df = DF()
    total_launch_done_df = DF()
    launch_dict = {}
    done_dict = {}
    rate_d = {}

    for k in launch_df.keys():
        launch_merge_df = pd.concat((launch_merge_df,launch_df[k]))
        ##dict for chn_risk.
        launch_df[k]["cycle"] = launch_df[k]["cycle"].astype(int)
        launch_dict[k] = launch_df[k]["cycle"].values.tolist()
    launch_merge_df["launch_cycle"] = launch_merge_df["cycle"].astype(int) ##astype&drop:1.for calculate. 2.cmd/done 'cycle' name conflict
    launch_merge_df.drop('cycle', axis=1, inplace = True)
    launch_merge_df = launch_merge_df.reset_index()
    launch_merge_df = launch_merge_df[launch_merge_df['index'].astype(int)%4 ==0] ##1. 4cycle,1 cmd. 2.original index type:'Int64Index'
    launch_merge_df.drop('index', axis=1, inplace = True)

    for i in done_df.keys():
        done_merge_df = pd.concat((done_merge_df,done_df[i]))
        ##dict for chn_risk.
        done_df[i]["cycle"] = done_df[i]["cycle"].astype(int)
        done_dict[i] = done_df[i]["cycle"].values.tolist()
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)

    total_launch_done_df = pd.merge(launch_merge_df, done_merge_df, how='outer')

    total_launch_done_df['latency'] = total_launch_done_df['done_cycle'] -  total_launch_done_df['launch_cycle']

    ave_latency = total_launch_done_df['latency'].mean()
    max_latency = total_launch_done_df['latency'].max()
    min_latency = total_launch_done_df['latency'].min()
    median_latency = total_launch_done_df['latency'].median()
    
    max_index = total_launch_done_df[total_launch_done_df['latency']==max_latency].index.min()
    min_index = total_launch_done_df[total_launch_done_df['latency']==min_latency].index.min()
    median_index = total_launch_done_df[total_launch_done_df['latency']==median_latency].index.min()

    max_inst_id = total_launch_done_df.loc[max_index,'inst_id']
    min_inst_id = total_launch_done_df.loc[min_index,'inst_id']
    median_inst_id = total_launch_done_df.loc[median_index,'inst_id']
    max_dbg_id = total_launch_done_df.loc[max_index,'dbg_id']
    min_dbg_id = total_launch_done_df.loc[min_index,'dbg_id']
    median_dbg_id = total_launch_done_df.loc[median_index,'dbg_id']

    rate_d = {'max_latency':max_latency, 'min_latency':min_latency, 'ave_latency':ave_latency, 
              'max_inst_id':max_inst_id, 'max_dbg_id':max_dbg_id, 
              'min_inst_id':min_inst_id, 'min_dbg_id':min_dbg_id,
              'median_latency':median_latency,
              'median_inst_id':median_inst_id, 'median_dbg_id':median_dbg_id}

    rate_d['rate'] = rate_d['ave_latency'].astype(int)  ##latency: int.

    rate_launch_d = util.get_rate(launch_dict, algo_algo)
    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_1 = util.get_channel_req_ratio(launch_df.keys(), launch_df, rate_launch_d, edir, 0.8, 1.2)
    risk_2 = util.get_channel_req_ratio(done_df.keys(), done_df, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] =(risk_1 or risk_2) ##True or False.

    return rate_d

def sqta_tdsq_avg(algo, edir, desc, warmup):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    warmup = 0
    algo_name, algo_algo = algo['algorithm'].split('@')
    start_cycles_num = util.get_start_cycles(edir, warmup)
    fld_cmd = dict(send = None, dbg_id = None, inst_id = None, cycle = {'start_cycles':start_cycles_num})       ##cmd signal 'send', cycle&id is common.
    fld_done = dict(valid = None, dbg_id = None, inst_id = None, cycle = {'start_cycles':start_cycles_num})     ##done signal 'valid', cycle&id is common.

    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    
    launch_df = util.get_fields(edir, desc[launch_vec], desc[launch_ptn] , fld_cmd)
    done_df = util.get_fields(edir, desc[done_vec], desc[done_ptn] , fld_done)

    launch_merge_df = DF()
    done_merge_df = DF()
    total_launch_done_df = DF()
    launch_dict = {}
    done_dict = {}
    rate_d = {}

    for k in launch_df.keys():
        launch_merge_df = pd.concat((launch_merge_df,launch_df[k]))
        ##dict for chn_risk.
        launch_df[k]["cycle"] = launch_df[k]["cycle"].astype(int)
        launch_dict[k] = launch_df[k]["cycle"].values.tolist()
    launch_merge_df["launch_cycle"] = launch_merge_df["cycle"].astype(int) ##astype&drop:1.for calculate. 2.cmd/done 'cycle' name conflict
    launch_merge_df.drop('cycle', axis=1, inplace = True)
    launch_merge_df = launch_merge_df.reset_index()
    launch_merge_df = launch_merge_df[launch_merge_df['index'].astype(int)%4 ==0] ##1. 4cycle,1 cmd. 2.original index type:'Int64Index'
    launch_merge_df.drop('index', axis=1, inplace = True)

    for i in done_df.keys():
        done_merge_df = pd.concat((done_merge_df,done_df[i]))
        done_df[i]["cycle"] = done_df[i]["cycle"].astype(int)
        done_dict[i] = done_df[i]["cycle"].values.tolist()
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    

    total_launch_done_df = pd.merge(launch_merge_df, done_merge_df, how='outer')

    min_cycle = total_launch_done_df['launch_cycle'].min()
    max_cycle = total_launch_done_df['done_cycle'].max()
    ave_latency = max_cycle - min_cycle 

    max_index = total_launch_done_df[total_launch_done_df['done_cycle']==max_cycle].index.min()
    min_index = total_launch_done_df[total_launch_done_df['launch_cycle']==min_cycle].index.min()

    max_inst_id = total_launch_done_df.loc[max_index,'inst_id']
    min_inst_id = total_launch_done_df.loc[min_index,'inst_id']
    max_dbg_id = total_launch_done_df.loc[max_index,'dbg_id']
    min_dbg_id = total_launch_done_df.loc[min_index,'dbg_id']

    rate_d = {'avg_wave_lifetime':ave_latency,
              'max_cycle':max_cycle, 'min_cycle':min_cycle,
              'max_inst_id':max_inst_id, 'max_dbg_id':max_dbg_id, 
              'min_inst_id':min_inst_id, 'min_dbg_id':min_dbg_id}

    rate_d['rate'] = rate_d['avg_wave_lifetime'].astype(int)  ##latency: int.

    rate_launch_d = util.get_rate(launch_dict, algo_algo)
    rate_done_d = util.get_rate(done_dict, algo_algo)

    ## check the balance of access to different VECs.
    risk_1 = util.get_channel_req_ratio(launch_df.keys(), launch_df, rate_launch_d, edir, 0.8, 1.2)
    risk_2 = util.get_channel_req_ratio(done_df.keys(), done_df, rate_done_d, edir, 0.8, 1.2)
    ##rate_d["channel_risk"] =(risk_1 and risk_2) ##True or False.
    rate_d["channel_risk"] =(risk_1 or risk_2) ##True or False.

    return rate_d

def tcea_interface_measure(algo, edir, desc, warmup):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup = 0
    start_cycles_num = util.get_start_cycles(edir, warmup)
    second_dispatch_cycle = util.get_start_cycles(edir,1)
    fld= dict(tag=None, cycle={'start_cycles':start_cycles_num})
    #pdb.set_trace() 
    #if algo_name == 'eatc_rdret_muu':
    ret_cycle = {}                                        # for channel_risk. keep ret_d df.keep ret_cycle dict.
    if 'eatc_rdret' in algo_name:
        req_vec, ret_vec = algo['vec'].split(',')
        req_ptn, ret_ptn = algo['ptn'].split(',')
        vec_cycle_d = get_effective_tag_cycle(edir, warmup, desc, req_vec, ret_vec, req_ptn, ret_ptn, fld)
        merge_table = get_merge_table(vec_cycle_d)
        for k,v in vec_cycle_d.items():
            #vec_cycle_d[k] = v.loc[v["cycle"] < second_dispatch_cycle]
            vec_cycle_d[k] = v.loc[v["cycle"] > start_cycles_num]
            ret_cycle[k] = vec_cycle_d[k]["cycle"].values.tolist()
        rate_d = util.get_rate(ret_cycle, algo_algo)## vec_cycle_d is dic {vec_name0:cycle_list, vec_name1:cycle_list,....}, rate_d is dic like {'num': 20328, 'max': 48574, 'min': 29345, 'rate': 1.0571532580997451}
        #pdb.set_trace()
        rate_d["rate"] = rate_d["rate"]*desc['ea_tcc_rdret_data_bw']
    #elif algo_name == 'tcea_rdreq_muu':
    elif 'tcea_rdreq' in algo_name:
        vec_cycle_d = get_effective_cid_cycle(edir, warmup, desc, desc[algo['vec']], desc[algo['ptn']])## the value of algo['vec'] is 'tcea_rdreq_sim_vec' and desc[algo['vec']] is 'tc\\d+_ea\\d+_rdreq_sim.vec'
        for k,v in vec_cycle_d.items():
            v.drop(['tag','cid'],axis =1, inplace = True)
## value in cycle or size is string should transfer it to int
            vec_cycle_d[k]['cycle'] = v["cycle"].astype("int64")
            vec_cycle_d[k]['size'] = v["size"].astype("int64")
        merge_table = get_merge_table(vec_cycle_d)
        for k,v in vec_cycle_d.items():
            ret_cycle[k] = v["cycle"].values.tolist()
        rate_d = util.get_rate(ret_cycle, algo_algo)
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(vec_cycle_d.keys(), vec_cycle_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d

def tcea_rdreq_duty_measure(algo, edir, desc, warmup):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup = 0
    start_cycles_num = util.get_start_cycles(edir, warmup)
    fld= dict(tag=None, cycle={'start_cycles':start_cycles_num})
    rate_cycle_dict = {}                                        # for channel_risk. keep ret_d df.keep ret_cycle dict.
    total_cycle_list = []
    effective_cycle_list = []
    sigle_vec_ratio_list = []
    ##get_effective_cid_cycle, get req from tcp, drop req from sqc. 
    vec_cycle_d = get_effective_cid_cycle(edir, warmup, desc, desc[algo['vec']], desc[algo['ptn']])
    vec_cycle_d_key = sorted(vec_cycle_d.keys())
    merge_df = DF()
    for k in vec_cycle_d_key:
        merge_df = vec_cycle_d[k]
        rate_cycle_dict[k] = merge_df['cycle'].astype(int).values.tolist()
        min_cycle = merge_df['cycle'].astype(int).min()
        max_cycle = merge_df['cycle'].astype(int).max()
        req_first_to_last_cycle = max_cycle - min_cycle
        efct_num = merge_df['cycle'].shape[0]   ##get row num as efct_num.
        sigle_vec_ratio = round((efct_num/req_first_to_last_cycle),2)
        total_cycle_list.append(req_first_to_last_cycle)
        effective_cycle_list.append(efct_num)
        sigle_vec_ratio_list.append(sigle_vec_ratio)

    total_cycle = sum(total_cycle_list)
    effective_cycle = sum(effective_cycle_list)
    ratio = round((effective_cycle/total_cycle),2)

    print('total_cycle is %d.' % total_cycle)
    print('effective_cycle is %d.' % effective_cycle)
    print('total duty cycle is %f.' % ratio)
    print('each vec duty cycle is :')
    print(sigle_vec_ratio_list)
    
    rate_d = util.get_rate(rate_cycle_dict, algo_algo)
    rate_d["rate"] = ratio 
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(vec_cycle_d.keys(), vec_cycle_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d



def get_effective_cid_cycle(edir, warmup, desc, vec, ptn):
    start_cycles_num = util.get_start_cycles(edir, warmup)
    fld = dict(tag = None, size = None, cid = {'valid_cid': [8]}, cycle = {'start_cycles':start_cycles_num})
    #if you need this columns but no filter value,A = None,else write a dict like B={key:value}
    req_d = util.get_fields(edir, vec, ptn, fld)
    ##according to field to get interface data form a rdreq-dict like dict = {'vec':DF,'vec1':DF1,...}
    return req_d

def get_effective_tag_cycle(edir, warmup, desc, req_vec, ret_vec, req_ptn, ret_ptn, fld):
#    req_vec, ret_vec = algo['vec'].split(',')
#    req_ptn, ret_ptn = algo['ptn'].split(',')
    #pdb.set_trace()
    req_vec = desc[req_vec]
    ret_vec = desc[ret_vec]
    req_ptn = desc[req_ptn]
    ret_ptn = desc[ret_ptn]
    ret_d = util.get_fields(edir, ret_vec, ret_ptn, fld)
    req_d = get_effective_cid_cycle(edir, warmup, desc, req_vec, req_ptn)
    final_data = {}
    for k in ret_d.keys():
        ret_tc_num = k.split('_')[1]
        if len(ret_d[k]) != 0:
            for k1 in req_d.keys():
                req_tc_num = k1.split('_')[0]
                # according to req.vec(tc1_ea1_rdreq_sim.vec) name and ret.vec (ea1_tc1_rdret_sim.vec) name to get req_tc and ret_tc ,compare data from the same request
                if ret_tc_num == req_tc_num and len(req_d[k1]) != 0:     
                    final_data[k] = DF()
                ##compare value(DF[tag]) of each key corresponding tc0_ea0_rdreq.vec and ea0_tc0_rdret.vec by comparing tc0 in tc0_ea0_rdreq.vec with tc0 in ea0_tc0_rdret.vec
                   # pdb.set_trace() ## for pdb debug
                    ret_d[k] = ret_d[k][ret_d[k]['cycle']>req_d[k1]['cycle'].min()]
                    ret_d[k] = keep_same_tag(req_d[k1],ret_d[k])
                    ret_d[k]['size'+'_'+ret_tc_num.strip('tc')] = ret_d[k]['size'].apply(lambda x: 32 if x == '0' else 64)
                    ##due to ret_d[k] has no column of 'size', so assign req_d[k1]['size'] to ret_d[k]['size']
                    ret_d[k].drop('size', axis = 1, inplace= True)
                    #ret_d[k]['size'] = ret_d[k]['data'].apply(lambda y : 32 if re.match(r'((x{8}\s){8}[^x]+)',y) else 64)
                    final_data[k] = ret_d[k]
                else:
                    continue
        else:
            continue
    return final_data


def keep_same_tag(req_df,ret_df):
    """
    The following functons is used to delete the TAG sent by CPC or CPG.. in rdret.vec file that is the same as the TAG 
    which is send by TCP because we need to compare rdreq.vec effective TAG and rdret.vec TAG ,SO we need remove rdret.vec's TAG from CPC/CPG
    this function compares the values of req's tag list and ret's tag list separately, 
    retaining the same value in ret and also retain the cycle value in ret that corresponds to the tag
    purpose delete the tag at the end of the ret.vec file that is same as the tag in req.vec but is invalid
    req_tag = [tag1,tag2...] ret_tag = [tag0,tag1,tag2...] ret_cycle = [c0,c1,c2...] eret_cycle = [c1,c2...]
    """
    req_tag = req_df['tag'].tolist()
    ret_tag = ret_df['tag'].tolist()
    ret_cycle = ret_df['cycle'].tolist()
    ret_tag_model = ret_df['tag'].tolist()
    # can not use ret_tag_model = ret_tag because when use pop in next step it will change ret_tag_model and ret_tag at a same time 
    eret_cycle = []
    for i in ret_tag:
        if i in req_tag:
            req_tag.pop(req_tag.index(i))
            eret_cycle.append(int(ret_cycle.pop(ret_tag_model.index(i))))
            ret_tag_model.pop(ret_tag_model.index(i))
            """
            In the for loop ,ret_tag's number can not be changed, so use ret_tag_model list to replace reg_tag ,when match a value,pop it in ret_tag_model
            put the same place's value in ret_cycle to eret_cycle and pop the value from ret_cycle to make ret_tag_model has the same number with ret_cycle
            in order to get the corresponing tag-cycle
            """
        else:
            pass
    eret_df = DF({'cycle':eret_cycle,'size':req_df['size']})
    return eret_df

def get_merge_table(vec_cycle_d):
    """
    completed mtab_df is a dataframe which columns have 'cycle' and 'size0','size1'...'size31'
    at a given cycle vec0-31's size ,possible size value is 32/64/Nan
    completed ttab_df is dataframe which columns have 'cycle'(unique),'total_size'
    (sum of 32 vec's size at a given cycle),'req_num'
    mtab_df: size0 size1 ... size31 cycle  ttab_df: req_num total_size cycle
              64    32   ...   64    333               3       160      333
              ..    ..   ...   ...   ...              ...      ...      ...
    add the size values of the same cycle in the 32 vec files,
    and then sum the size of the window period of a certain cycle 
    that is bandwidth in the current time period(total_szie),while req is the 
    number of requests inthis time period(req_num),the rate is total_size/wd
    merge_table_df:    req_num    total_size    wd       rate
                          20         1280       0-100     12.8
                          ..           ..      100-200    ..
    """
    mtab_df=DF([],columns=('cycle','size'))
    ttab_df = DF()
    for v in vec_cycle_d.values():
        mtab_df = pd.merge(mtab_df,v,on = 'cycle', how = 'outer')
    ttab_df['cycle'] = mtab_df['cycle']
    ttab_df['total_size'] = mtab_df.apply(lambda x: x.sum(),axis=1)-mtab_df['cycle']
    #get the sum of the values of non-Nan in each row and assign to total_size
    ttab_df['req_num'] = len(mtab_df.columns)-mtab_df.isnull().sum(axis=1)-1
    #cal the sum of the number of non-Nan in each row assign to req_num 
    ttab_df.sort("cycle",inplace = True)
    merge_table_df = DF(index=(range(0,20)),columns = ('req_num','total_size','wd'))
    d = int((ttab_df['cycle'].max()-ttab_df['cycle'].min())/20)
    m = int(ttab_df['cycle'].min())
    for i in range(0,20):
        merge_table_df['total_size'][i] = ttab_df.loc[ttab_df['cycle'].isin(range(m+d*i,m+d*(i+1)))]['total_size'].sum()
        #calculate the sum of all size in a cycle period like cycle[0-100]
        merge_table_df['req_num'][i] = ttab_df.loc[ttab_df['cycle'].isin(range(m+d*i,m+d*(i+1)))]['req_num'].sum()
        #calculate the sum of all req_num in a cycle period like cycle[0-100]
        merge_table_df['wd'][i] = str(m+d*i)+'-'+str(m+d*(i+1))
    merge_table_df['rate'] = merge_table_df['total_size']/d

    return merge_table_df



############## for tcc_tcr_rdata interface measure##########
def tcctcr_interface_measure(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles_number = util.get_start_cycles(edir, warmup)
    fld = dict(send = None, send_128B = None, dst_sel = None,cycle = {'start_cycles':warmup_start_cycles_number})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld) ## dict is {tcp1_tcr_req_sim.vec: DF,tcp2_tcr_req_sim.vec : DF,....}

    tem_cnt = 0
    ret_cycle = {}
    for k in ret_d.keys():
        # filter out invalid data
        ret_d[k]["dst_sel"] = ret_d[k]["dst_sel"].map(lambda x: int(x,16))
        ret_d[k] = ret_d[k].loc[ret_d[k]["dst_sel"] <= desc['client_id_is_tcp']]
        ret_d[k] = ret_d[k].loc[ret_d[k].send.isin(["1"])]
        #retain data from TCP, convert 'dst_sel' to hex and keep the value is less than 0x58
        ret_d[k] = ret_d[k].astype(int)
        
        # send signal is limited to 1, so we can just use send_128B to get the req size
        # send_128B = 1 means 128B request while send_128B = 0 means 64B request
        ret_d[k]["data_size"] = (ret_d[k]["send_128B"] + 1) * 64

        # merge all of info in every vec to a table, in order to get the mean request size to deal with both 128 and 64 exist in test
        if tem_cnt == 0:
            total_data = ret_d[k]
        else:
            total_data = pd.concat((total_data, ret_d[k]))
        tem_cnt += 1
        
        # use dict-ret_cycle as the para for get_rate function to calc the rate
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    rate_d = util.get_rate(ret_cycle, algo_algo)
    
    # window
    condition_cycle = (total_data['cycle'] >= rate_d['min']) & (total_data['cycle'] <= rate_d['max'])
    final_data = total_data[condition_cycle]   
    
    rate_d["rate"] = round(rate_d["rate"] * final_data["data_size"].mean())

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    
    return rate_d

############## for tcr_tcc_wdata interface measure##########
def tcrtcc_interface_measure(algo, edir, desc, warmup=1):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    
    warmup_start_cycles_number = util.get_start_cycles(edir, warmup)
    
    fld = dict(send = None, dst_sel = None,cycle = {'start_cycles':warmup_start_cycles_number})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld) ## dict is {tcp1_tcr_req_sim.vec: DF,tcp2_tcr_req_sim.vec : DF,....}
    ret_cycle = {}                                          # for channel_risk. keep ret_d df.keep ret_cycle dict.
    for k in ret_d.keys():
        #retain data from TCP, convert 'dst_sel' to hex and keep the value is less than 0x58
        ret_d[k]["dst_sel"] = ret_d[k]["dst_sel"].map(lambda x: int(x,16))
        ret_d[k] = ret_d[k].loc[ret_d[k]["dst_sel"] <= desc["client_id_is_tcp"]]
        ret_d[k] = ret_d[k].loc[ret_d[k].send.isin(["1"])]
        ret_d[k] = ret_d[k].astype(int)
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()

    rate_d = util.get_rate(ret_cycle, algo_algo)
    rate_d["rate"] = rate_d["rate"] * desc['tcr_tcc_wdata_data_bw'] * desc['tcr_tcc_wdata_bus']

    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

#def get_tcctcr_measure_rate(ret_d):
#    merge_df = DF()
#    min_li   = []
#    max_li   = []
#    for v in ret_d.values():
#        merge_df = pd.concat([merge_df,v], axis=0, ignore_index = True)
#        min_li.append(int(v["cycle"].min()))
#        max_li.append(int(v["cycle"].max()))
#    merge_df = merge_df.astype(int)
#    merge_df["send_128B"] = merge_df["send_128B"].apply(lambda x: 64 if x == '0' else 128)
#    merge_byte = merge_df["send_128B"].sum(axis=0)
#    merge_num = len(merge_df[(merge_df["cycle"] < max(max_li))&(merge_df["cycle"] > min(min_li))])
#    merge_measure_rate = merge_byte/(max(max_li) - min(min_li))
#    rate_d ={"max": max(max_li), "min": min(min_li), "rate":merge_measure_rate, "num":merge_num}   ##Todo need to update a new mode to calculate for tcctcr_interface and for unit is Byte to function "get_rate()" in measure_util.py
#   return rate_d 

def chk_td_swiz_in_mtx_cpy(edir, desc, kind):
    '''
    :kind: 'b16_lds', 'b8_lds', 'b16_vgpr'
    '''
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    pmlog = util.PMLog('check_td_swizzling_in_matrix_copy')
    bits,tgt = kind.split('_')
    #Get TC_TD_DATA
    tctd_fld = oodict(ls_ooo=None,data=None,dbg_id=None,cycle=None)
    tctd_data = util.get_fields(edir, desc['tctd_data_sim_vec'], desc['tctd_vld_data'], tctd_fld)
    #Get TD_SP_DATA
    tdsp_fld = dict(we=None,data=None,pkt_type=None,lds_req=None,dbg_id=None,cycle=None)
    tdsp_data = util.get_fields(edir, desc['tdsp_data_sim_vec'], desc['tdsp_vld_data'], tdsp_fld)

    def get_dwd_per_inst_tdsp(td_id, dbg_id):
        '''
        :return: list of dwords of one instruction has the same debug_id
        '''
        for k, v in tdsp_data.items():
            ##td-sp-data
            g_ = re.search(r'se(\d)__sh0td(\d+)', k).groups()
            dwd = []
            if td_id == int(g_[0])*int(desc['cu/se']) + int(g_[1]):
                idata = v[v['dbg_id'].isin([dbg_id])]['data']
                for d in idata:
                    dwd_ = d.split('_')
                    _l = []
                    [_l.extend(re.findall('.{4}', x)) for x in dwd_]
                    dwd.append(_l)
                return dwd

    caled_tdsp = {}
    for vec, vdata in tctd_data.items():
        idata = {}
        caled_data = {}
        for id in vdata['dbg_id'].unique():
            ##no to_list() of Series of this version of pandas and list() also results in error
            idata[id] = vdata[vdata['dbg_id'].isin([id])]['data']
        for id,da in idata.items():
            datum = {'low': [], 'high':  []}
            dlow, dhigh = [], []
            for row,drow in enumerate(da):
                dwords = drow.split('_') 
                dwords.reverse() #original string has msb on the most-left
                for clm,dclm in enumerate(dwords):
                    if bits == 'b16':
                        _h,_l = re.findall('.{4}', dclm)
                    datum['low'].append(_l)
                    datum['high'].append(_h)
            for k in datum.keys():
                d_ = datum[k]
                d_ = [d_[i:i+32] for i in range(0, len(d_), 32)]
                for i in range(0, len(d_), 4):
                    merged = list(zip(d_[i+3], d_[i+2], d_[i+1], d_[i]))
                    merged = [''.join(s) for s in merged]
                    merged = [re.findall(r'.{4}', i) for i in merged]
                    [v.reverse() for v in merged]
                    if k=='low': dlow.append(merged)
                    if k=='high': dhigh.append(merged)
            swizzled = [] #One matrix copy instruction
            for i,vl in enumerate(dlow):
                _s = []
                for j,vll in enumerate(vl):
                    _s.append(vll + dhigh[i][j])
                for i in range(0, len(_s), 4):
                    _ss = _s[i]+_s[i+1]+_s[i+2]+_s[i+3]
                    _ss.reverse()
                    swizzled.append(_ss)
            sent_tdsp = get_dwd_per_inst_tdsp(int(re.search(r'tc_td(\d+)_data', vec).group(1)), id)
            errors = 0
            for i, row_data in enumerate(sent_tdsp):
                for j, element_data in enumerate(row_data):
                    if int(element_data, 16) != int(swizzled[i][j], 16):
                        pmlog.error("tdsp[%d][%d]: %s != swizzled[%d][%d]: %s", i, j, element_data, i, j, swizzled[i][j])
                        errors += 1
                        if errors > 10 : 
                            print("[chk_td_swiz_in_mtx_cpy]Too many errors. QUIT")
                            sys.exit()
    return True
                        
########For TCP_TD_data interface measure########
def tcptd_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    
    warmup_start_cycles = util.get_start_cycles(edir,warmup)
    
    fld = dict(send = None, data = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)
    
    data_vec_cnt = 0
    ret_cycle = {}
    for k in ret_d.keys():
        ret_d[k] = ret_d[k].loc[ret_d[k].send.isin(["1"])]
        ret_d[k]['cycle'] = ret_d[k]['cycle'].astype(int)

        # merge all of data in every vec to a table, in order to get the mean request size to deal with both 128 and 64 exist in test
        if data_vec_cnt == 0:
            total_data = ret_d[k]['data']
        else:
            total_data = pd.concat((total_data, ret_d[k]['data']))
        data_vec_cnt += 1
        
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    
    # window
    total_data['bw'] = 1 - (total_data.str.count("x") / (desc['tcp_td_data_data_bw'] * 8 / 4))

    rate_d = util.get_rate(ret_cycle, algo_algo)
    rate_d["rate"] = rate_d["rate"] * total_data['bw'].mean() * desc['tcp_td_data_data_bw'] * desc['tcp_td_data_bus']
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    
    return rate_d

########For TD_SP_data interface_measure#########
def tdsp_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(valid = None, cycle = {"start_cycles":warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)
    ret_cycle = {}
    for k in ret_d.keys():
        #remove the value where valid is 0 to keep valid value
        ret_d[k] = ret_d[k].loc[ret_d[k].valid.isin(["1"])]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    rate_d = util.get_rate(ret_cycle, algo_algo)
    rate_d["rate"] = rate_d["rate"] * desc['td_sp_data_bus'] * desc['td_sp_data_data_bw']
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d

########For TCP_TCR_req interface measure#########
def tcptcr_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'
    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(cycle = {"start_cycles":warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)
    ret_cycle = {}
    for k in ret_d.keys():
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    rate_d = util.get_rate(ret_cycle, algo_algo)
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.
    return rate_d

########For SQ_TA_cmd interface_measure#########
def sqta_cmd_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(send = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)
    ret_cycle = {}
    for k in ret_d.keys():
        #remove the value where valid is 0 to keep valid value
        ret_d[k] = ret_d[k].loc[ret_d[k].send.isin(["1"])]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    rate_d = util.get_rate(ret_cycle, algo_algo)

    ipw = int(re.search(r'.*perf.*ipw(\d+).*', edir).group(1))      # get the inst per wave from the testname in edir
    rate_d["rate"] = rate_d["rate"] / 4 * 64 / ipw                  # translate the unit to thread per cycle, 64 means thread/wave, 4 means the effective signal per inst
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

########For SQ_TA_cmd interface_measure#########

########For TA_TCP_addr interface_measure#########
def tatc_addr_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    algo_name, algo_algo = algo['algorithm'].split('@')
    warmup_start_cycles = util.get_start_cycles(edir, warmup)
    fld = dict(send = None, state_read = None, cycle = {"start_cycles": warmup_start_cycles})
    vec = desc[algo['vec']]
    ptn = desc[algo['ptn']]
    ret_d = util.get_fields(edir, vec, ptn, fld)
    ret_cycle = {}
    for k in ret_d.keys():
        #remove the value where valid is 0 to keep valid value
        ret_d[k] = ret_d[k].loc[ret_d[k].send.isin(["1"])]
        ret_d[k] = ret_d[k].loc[ret_d[k]["state_read"] == "1"]
        ret_d[k] = ret_d[k].astype(int)
        #transform the value of ret_d to a list which is just include cycle
        ret_cycle[k] = ret_d[k]["cycle"].values.tolist()
    rate_d = util.get_rate(ret_cycle, algo_algo)

    if 'structure_buffer' in edir:
        dwpi = int(re.search(r'.*perf.*dwordx(\d+).*', edir).group(1))
        ipw = 32/dwpi
    else:
        ipw = int(re.search(r'.*perf.*ipw(\d+).*', edir).group(1))      # get the inst per wave from the testname in edir
    rate_d["rate"] = rate_d["rate"] * 64 / ipw                  # translate the unit to thread per cycle, 64 means thread/wave, 4 means the effective signal per inst
    ## check the balance of access to different VECs. 
    rate_d["channel_risk"] = util.get_channel_req_ratio(ret_d.keys(), ret_d, rate_d, edir, 0.8, 1.2) ##True or False.

    return rate_d

########For SQ_TA_cmd interface_measure#########


def tcea_latency_measure(algo, edir, warmup):
#NOTICE This function should use next command for pandas edition
#/usr/bin/env python3 -m pdb cache_measure.py
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    start_cycles_num = util.get_start_cycles(edir, warmup)
    fld = dict(tag = None, cycle = {'start_cycles':start_cycles_num})

    launch_vec, done_vec = algo['vec'].split(',')
    launch_ptn, done_ptn = algo['ptn'].split(',')
    if ("load" in edir):
        launch_d = util.get_fields(edir, "tc\d+_ea\d+_rdreq_sim.vec", "TC\d+_EA\d+_rdreq\s\d\s\d(\s\w+)+", fld)
        done_d = util.get_fields(edir, "ea\d+_tc\d+_rdret_sim.vec", "EA\d+_TC\d+_rdret\s\d\s\d(\s\w+)+", fld)
        #launch_d = util.get_fields(edir, "tc7_ea7_rdreq_sim.vec", "TC\d+_EA\d+_rdreq\s\d\s\d(\s\w+)+", fld)
        #done_d = util.get_fields(edir, "ea7_tc7_rdret_sim.vec", "EA\d+_TC\d+_rdret\s\d\s\d(\s\w+)+", fld)
    else:
        launch_d = util.get_fields(edir, "tc\d+_ea\d+_wrreq_sim.vec", "TC\d+_EA\d+_wrreq\s\d\s\d(\s\w+)+", fld)
        done_d = util.get_fields(edir, "ea\d+_tc\d+_wrret_sim.vec", "EA\d+_TC\d+_wrret\s\d\s\d(\s\w+)+", fld)
    launch_merge_df = DF()
    done_merge_df = DF()
    
    launch_d_key = sorted(launch_d.keys())
    done_d_key = sorted(done_d.keys())
    lifetime_range_list = []
    # merge launch df and rename cycle to launch_cycle
    for k in launch_d_key:
        #launch_merge_df = pd.concat((launch_merge_df, launch_d[k]))
        launch_merge_df = launch_d[k]
        launch_merge_df = launch_merge_df.sort_values(by = ['tag','cycle'])
        launch_merge_df = launch_merge_df.reset_index()
        done_merge_df = done_d[done_d_key[launch_d_key.index(k)]]
        done_merge_df = done_merge_df.sort_values(by = ['tag','cycle'])
        done_merge_df = done_merge_df.reset_index()
        launch_merge_df["cycle"] = launch_merge_df["cycle"].astype(int)
        done_merge_df["cycle"] = done_merge_df["cycle"].astype(int)
        #launch_merge_df.drop('cycle', axis=1, inplace = True)
        #done_merge_df.drop('cycle', axis=1, inplace = True)
        lifetime_range_list.extend(done_merge_df["cycle"] - launch_merge_df["cycle"])
    # merge done df and rename cycle to done_cycle
    """for k1 in done_d_key:
        done_merge_df = pd.concat((done_merge_df, done_d[k1]))
    done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
    done_merge_df.drop('cycle', axis=1, inplace = True)
    # merge launch_df and done_df and the same dbg_id will automatically merged together
    total_launch_done_df = pd.concat([launch_merge_df, done_merge_df], axis=1)
    
    lifetime_range_lst = total_launch_done_df["done_cycle"] - total_launch_done_df['launch_cycle']"""

    rate_d = {'max_cycle':max(lifetime_range_list), 'min_cycle':min(lifetime_range_list), 'ave_cycle':sum(lifetime_range_list)/len(lifetime_range_list)}
    cycle1 = sum(i <= 1000 for i in lifetime_range_list)
    cycle2 = sum(i>1000 and i<=2000 for i in lifetime_range_list)
    cycle3 = sum(i>2000 and i<=3000 for i in lifetime_range_list)
    cycle4 = sum(i>3000 for i in lifetime_range_list)
    return rate_d


def tcea_rd_latency(algo, edir, desc, warmup):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    start_cycles_num = util.get_start_cycles(edir, warmup)
    fld = dict(tag = None, cycle = {'start_cycles':start_cycles_num})

    send_vec, done_vec = algo['vec'].split(',')
    send_ptn, done_ptn = algo['ptn'].split(',')

    send_d = util.get_fields(edir, desc[send_vec], desc[send_ptn], fld)
    send_merge_df = DF()

    done_d = util.get_fields(edir, desc[done_vec], desc[done_ptn], fld)
    done_merge_df = DF()
    
    total_df = DF()

    send_d_key = sorted(send_d.keys())
    done_d_key = sorted(done_d.keys())
    send_done_latency_list = []
    for k in done_d_key:
        ############
        done_merge_df = done_d[k]
        done_merge_df = done_merge_df.sort(columns = ['tag'])
        done_merge_df = done_merge_df.reset_index()
        ##tag ---> new_tag, encode each req&ret
        done_merge_df['tag_cnt'] = done_merge_df.groupby('tag').cumcount()
        done_merge_df['new_tag'] = done_merge_df['tag'] + '_' + done_merge_df['tag_cnt'].astype(str)
        ##
        send_merge_df = send_d[send_d_key[done_d_key.index(k)]]
        send_merge_df = send_merge_df.sort(columns = ['tag'])
        send_merge_df = send_merge_df.reset_index()
        send_merge_df['tag_cnt'] = send_merge_df.groupby('tag').cumcount()
        send_merge_df['new_tag'] = send_merge_df['tag'] + '_' + send_merge_df['tag_cnt'].astype(str)
        ##
        send_merge_df["send_cycle"] = send_merge_df["cycle"].astype(int)
        done_merge_df["done_cycle"] = done_merge_df["cycle"].astype(int)
        send_merge_df.drop(['index','tag','tag_cnt'], axis=1, inplace = True)
        done_merge_df.drop(['index','tag','tag_cnt'], axis=1, inplace = True)
        ##merge shared ROW on key, drop diff ROW.
        mg_df = pd.merge(done_merge_df,send_merge_df,on = 'new_tag',how='inner')
        mg_df['latency'] = mg_df['done_cycle'] - mg_df['send_cycle']
        total_df = pd.concat((total_df,mg_df))

    total_df = total_df.reset_index()

    rate_d = {}
    print('[tcea_req_ret_latency]:')
    ## check if total_df['latency'] 
    if total_df['latency'].isnull().any():
        print('**Error: scenario does not exit.**')
    else:
        rate_d['max_cycle'] = total_df['latency'].max() 
        rate_d['min_cycle'] = total_df['latency'].min()
        rate_d['ave_cycle'] = total_df['latency'].mean()
        rate_d['median_cycle'] = total_df['latency'].median()
        rate_d['rate'] = rate_d['ave_cycle']

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
    
    return rate_d

def pfct_tcc_bfld_interface_measure(algo, edir, desc, warmup = 0):
    if not os.path.isdir(edir):
        return None, 'edir is not valid directory'

    vec = desc[algo['vec']] 
    vfiles = util.file_finder(edir, vec)                                          # get all of vec files.
    vec_data = {} 
    dict = {}
    wave_rate = {}
    hit_rate_l = []
    miss_rate_l = []
    rate_d = {}
    for f in vfiles:
        ptn_dtype = {'pfct_key': str, 'vaule': str}                          # str: to delete '\t'
        vec_data = pd.read_csv(edir + f, header=3 ,usecols=[0,1], names=['pfct_key','vaule'], dtype=ptn_dtype)
        vec_data['vaule'] = vec_data['vaule'].str.strip()
        vec_data['vaule'] = vec_data['vaule'].str.replace('\t','')
        vec_data['vaule'] = vec_data['vaule'].str.replace("'","")
        vec_data['vaule'] = vec_data['vaule'].str.replace('"','')
        vec_data['vaule'] = vec_data['vaule'].astype(float)
        dict = vec_data.set_index('pfct_key')['vaule'].to_dict()             # common process:vec-df-dict.
        hit_rate = dict['hit'] / dict['req']
        hit_rate_l.append(hit_rate)
        miss_rate = dict['miss'] / dict['req']
        miss_rate_l.append(miss_rate)

    avg_hit_rate = sum(hit_rate_l) / float(len(hit_rate_l))
    avg_miss_rate = sum(miss_rate_l) / float(len(miss_rate_l))
    
    rate_d['rate'] = avg_hit_rate
    rate_d['hit_rate'] = avg_hit_rate
    rate_d['miss_rate'] = avg_miss_rate
    rate_d['normal_evict'] = dict['normal_evict']
    
    return rate_d

if __name__=='__main__':
    algo ={
        'unit'              : "Byte/cycle"
        ,'formula'          : "sum(BYTEn)/(max(RDRETn)-min(RDRETn))"
        ,'algorithm'        : "eatc_rdret_mun@merge_uniform_normal"
        ,'measure'          : "tcea_interface_measure"
        ,'vec'              : "tcea_rdreq_sim_vec,eatc_rdret_sim_vec"
        ,'ptn'              : "tcea_rdreq_ptn,eatc_rdret_ptn"
    }
    #edir = '/project/bowen/a0/arch/corepv/bowena0_pv_regr_0308/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/run/block/perf/perf_buffer_load_dwordx4_comp1_hitTCC_ipw48_wpg4/'
    edir = '/project/bowen/a0/arch/corepv/bowen_soc_0829/out/linux_3.10.0_64/vega20c/config/chip_gc_perf/run/block/perf/perf_global_load_dwordx4_hitMEM_ipw48_wpg4/'
    warmup = 0
    tcea_latency_measure(algo,edir,warmup)
    """desc = util.get_desc('bowen_ip', 'measure')
    warmup =0
    tcea_interface_measure(algo, edir, desc, warmup)"""
    """
    outh = '/project/bowen/a0/gfxdv/lilizhao/bowena0_gc_dev/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/run/block/perf/'
    edir = outh + 'perf_matrix_load_b16_swON_rROW_tCOL_lds'
    desc = util.get_desc('bowen_ip', 'measure') 
    chk_td_swiz_in_mtx_cpy(edir, desc, 'b16_lds')
    """
    pass

