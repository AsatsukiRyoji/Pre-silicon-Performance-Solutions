#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Performance Theory Model
@author: Li Lizhao, Guo Jiamin, Ma Xingxing

NOTE1. If a bus is data bus, it must be ended as '_(a-z)data', else DONT use it
NOTE2. Comparing in WPC, returned result in BPC or TPC per bottleneck
"""

import os,sys,re, pdb
from collections import OrderedDict as OD
#Limit the usage of pandas on kernel model since it's slow 
#on log-in server
#This version of Pandas couldn't support DataFrame.rename() well
#[XXX]In pandas, any Series/0 will be stored as 'inf' type automatically, 
#so we don't need to judge it manually
from pandas import DataFrame as DF
from pandas import Series as SE
import pandas as pd
import numpy as np

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir+'../')

import utility.util as util

##[XXX]A list to record all function names of CCT which is also used to 
##create a ordered dictionary
cct_func = [
    'cp_theory', 
    'spi_theory', 
    'sq_theory', 
    'sp_theory', 
    'lds_theory',
    'lds_latency_theory',
    #Logically CU has ta/td/tcp, but in RTL heirarchy, ta/td/tcp/tcc/tci/tca all in tc module
    'ta_theory',
    'tcp_theory',
    ##--Below function are invoked in tc_thoery
    'td_theory',
    'tcc_theory', 
    ##--
    'gds_theory',
    'gds_latency_theory',
    'ea_theory',
    'mem_theory'
]
##[XXX]
#When test performance model assembles meta per below keys, these keys 
#represent 'SINGLE INSTRUCTION' materials. The core theory model will take 
#care single-inst-multi-data part, like a vmem buffer_load_dword instruction 
#requests 1DW per thread, model will *threads/wave*ipw onto it
##[XXX]
##[XXX]The function names mapping with meta keys
##[XXX]Every meta key must be unique
##OD is required to keep order to facilitate further checking
cct_func_keys = OD(zip(cct_func, [ 
    ['wpg', 'pip', 'que', 'gpd'],                           # for cp theory
    ['vgpr', 'sgpr', 'wave', 'order'],                      # for spi theory
    ['valu', 'salu', 'lds', 'vmem', 'smem', 'branch'],      # for sq theory

    # for sp theory
    ##'vop' includes all instruction type of SP. The format of it should be 
    ##'[subtypeN]*ipw(|/(-/&))[subtypeN+1]*ipw(|/(-/&))...'. Use 'vop' on SP groups due to too many columns
    ##'|' is 'or', separating calculation and stored in different columns
    ##'-' is 'add', union calculation and stored in one column
    ##'&' is 'merge', like 'co-exec', the theory of merged ones use specific value from desc. and stored in one column
    ###A 'a-b&c' is a-(b&c), '(a-b)&c' is not one realizable design in ALU pipeline
    ##If only one subtype*ipw, the sp_exec_vop is default column name
    ##all subtype columns only contains ipw
    ##[XXX]'vop' type cannot be mixed with other ones
    ['vop', 'vop16', 'vop16_trans', 'vop16_pk', 'vop32', 'vop32_trans', 'vop64', 'vop64_trans', 'vop64_dp4xon', 'vop64_dppm', 'sgemm', 'dgemm', 'sgemm_vstep', 'dgemm_vstep', 'component', 'vmemPAY'],
    
    # for lds theory
    #iDS: instructionDS; sDS: sizeDS; cDS: conflictDS
    ['iDS', 'sDS', 'cDS', 'ds_PAY', 'sp_ds_PAY', 'ds_inst'],  #sDS: Set internally

    ['lds_inst_type'],      #for lds_latency_theory...if newly add theory. must add para
    
    ['vmemCOA'],            # for ta theory
    
    ##vmemTER: vmemTERminal[lds|vgpr](vmem instruction write or read terminal)
    ##vmemCOA: vmemCOAlesced
    ##vmemPAY: vmemPAYload(DWord per opcode in a shader)
    ##vmemCAC: vmemCAChe[tcp|tcc|mem](hit target)
    ['vmemCAC'],          # for tcp theory

    ##[XXX]If tc_theory keys are set from meta of test, the below ta/td, tcp and tcc part 
    ##[XXX]must not be set
    ##coa: coalesced; compN: componentNumber; dataF: dataFormat
    ['vmemTER'],        # for td theory
    
    ['vmemTYPE', 'vmemCAC'],        # for tcc theory
    ['bitwise', 'ipw', 'gds_wpg'],               # for gds_theory
    ['gds_inst_type'],              #for gds latency theory
    ['eaB'],                        # for ea theory
    ['memB']                        # for mem theory

]))

#Unit conversion
b2B = 0.125
B2b = 8
DW2B = 4
B2DW = 0.25

# the pipeline near the front has a higher priority
bottleneck_weight = {
    "dispatch_wave"     :   1,
    "alloc_wave_resource" :   2,
    "init_sgpr"         :   3,
    "init_vgpr"         :   4,
    "baton_limit"       :   5,
    "spisq_cmd"         :   6,
    "sq_ex_issue"       :   7,
    "sqsp_simd_src_d"   :   8,
    "sqsp_simd_src_c"   :   9,
    "sqta_cmd"          :   10,
    "sp_exec"           :   11,
    "spta_addr"         :   12,
    "spta_data"         :   13,
    "splds_idx"         :   14,
    "ldssp_read_data"   :   15,
    "lds_latency"       :   16,
    "tatcp_cmd"         :   17,
    "tatcp_addr"        :   18,
    "tatcp_data"        :   19,
    "tcptcr_req"        :   20,
    "tcptcr_hdata"      :   21,
    "tcrtcc_data"       :   22,
    "tccea_data"        :   23,
    "eatcc_data"        :   24,
    "tcctcr_data"       :   25,
    "tcrtcp_data"       :   26,
    "tcptd_data"        :   27,
    "tdsp_data"         :   28,
    "sxgds_data"        :   29,
    "gds_latency"       :   30
}

class ComputeCoreTheory:
    """
    Theory calculation is based on a scenario that 'payload is always full'.
    """

    ##def __init__(self,desc,test,meta_df,mode='WAVE'):
    def __init__(self,desc,meta_df,mode='WAVE'):
        """Compute Core Theory Model
        :mode: 1)WAVE: per-wave calculation
        """
        ##[FIXME]Some consideration on what should be 'self.'.
        #1)Datum passed as a part of this object for further usage
        #2)If feel bothering on 'self.', using an alias inside function to replace it 
        self.desc = util.get_desc(desc, 'theory')
        self.mode = mode
        self.bottleneck_l = []
        self.inter_only_col = []
        #[XXX]theo is initialized with meta_df but not self.meta to keep it clean to view
        self.meta = self.__preproc_meta(meta_df, self.desc, mode)
        self.theo = DF(meta_df) #XXX Any update of meta_df will also be get by theo
        ##self.test = test
        pass
    
    @staticmethod
    def parse_ds_inst(iDS):
        ptn = "([a-z_]+)(\d+)?_b(\d+)"
        inst, opN, opB = re.search(r''+ptn+'', iDS).groups()
        opN = 1 if opN == None else opN
        return b2B*int(opB)*int(opN)

    def __preproc_meta(self, meta, desc, mode):
        m, d = meta, desc
        if mode == 'WAVE':
            ##[XXX]'wpg' is 0 means no wave at all, else set 'wave' to 1 under mode=='WAVE'
            m['wave'] = m['wpg'].apply(lambda x: 1 if x!=0 else 0)
            self.inter_only_col.append('wave')
        if 'lds' in m.columns:
            m['sDS'] = m['iDS'].apply(lambda i: ComputeCoreTheory.parse_ds_inst(i))
            self.inter_only_col.append('sDS')
            #[XXX]The parsed inst will become 'read', 'write'... and that 
            #makes the 'read2' cannot be distinguished from 'read', so original iDS is reserved
        if ('vmem' in m.columns) or ('vmemPAY' in m.columns):
            m['vmem_workload'] = m['vmemPAY']*DW2B*m['vmem']*d['threads/wave']
            self.inter_only_col.append('vmem_workload')
        ##if ('ds_inst' in m.columns) or ('ds_PAY' in m.columns):
        if 'ds_PAY' in m.columns:
            m['ds_workload'] = m['ds_PAY']*m['ds_inst']*d['threads/wave']
            self.inter_only_col.append('ds_workload')
        ##if ('ds_inst' in m.columns) or ('sp_ds_PAY' in m.columns):
        if 'sp_ds_PAY' in m.columns:
            m['sp_ds_workload'] = m['sp_ds_PAY']*m['ds_inst']*d['threads/wave']
            self.inter_only_col.append('sp_ds_workload')

        
        return m
    
    def get_theory(self):
        """Get theory. Per column result is WPC, the final result is TPC or BPC
        """
        for k,v in cct_func_keys.items():
            vld = set(v).intersection(set(self.meta.columns))
            if len(vld)>0:
                #Keep every <block>_theory uses primitive desc so that they can
                #be invoked from external directly
                fn = 'self.'+k
                #self.theo is dealt inside every function
                eval(fn)(vld)
        candidates = self.theo.loc[:,self.bottleneck_l]
        candidates = candidates.replace(0, np.nan)
        cidx = list(candidates[candidates.apply(lambda x: x == x.min(), axis=1)].stack().index)
        ##Theory need to be attached before bottleneck
        self.theo['theory'] = candidates.apply(lambda x: x.min(), axis=1)
        #self.theo['bottleneck'] = candidates.idxmin(axis=1) #compare in all columns fro row direction
        #Find all potential bottlenecks, and prefer 'data' one than non-data ones
        bcandi = []
        for i in cidx:
            try:
                bcandi[i[0]].append(i[1])
            except:
                bcandi.insert(i[0], [i[1]])
        bottleneck = []

        for i in bcandi:
            if len(i) == 1:
                bottleneck.append(i[0])
                continue
            elif len(i) > 1:
                # the pipeline near the front has a higher priority
                i = sorted(i, key = lambda x: bottleneck_weight[x])
                bottleneck.append(i[0])
                continue
        
        ####name_dict = self.meta['name'].to_dict()
        ######a = name_dict['0'] ##{0: 'perf_latency_ds_write_b64_ipw4_wpg4'} not {'a':'b'} but {a:'b'},so we need  name_dict[0].
        ####a = name_dict[0]
        ####if 'latency_ds_' in a:
        ####    v = []
        ####    v.append('inst_type')
        ####    self.lds_latency_theory(v)
        ####    bottleneck.clear() ##if not,['spi_vdata', 'lds_latency']
        ####    bottleneck.append('lds_latency')

        """
        #bottleneck.append(bcandi[0][0])
        for bc in bcandi:
            for i, b in enumerate(bc):           # order by block, the privious block has higher priority
                bottleneck.append(b)
                break
        """
        """
        for bc in bcandi:
            for i,b in enumerate(bc):           # order by block, the privious block has higher priority
                if b.endswith('data') or i == len(bc)-1:
                    bottleneck.append(b)
                    break
        """
        self.theo = self.theo.join(DF(bottleneck, columns=['bottleneck']))
        self.theo['unit'] = ''
        def reunit(x):
            if x['bottleneck'] == 'init_sgpr':
                x['theory'] = x['theory']*x['sgpr_workload']
                x['unit'] = 'BPC'
            elif x['bottleneck'] == 'init_vgpr':
                x['theory'] = x['theory']*x['vgpr_workload']
                x['unit'] = 'BPC'
            elif x['bottleneck'] == 'spta_data':
                x['theory'] = round(x['theory']*x['std_workload'])
                x['unit'] = 'BPC'
            elif x['bottleneck'] == 'tatcp_data' \
                 or x['bottleneck'] == 'tcrtcp_data' \
                 or x['bottleneck'] == 'tcptcr_data' \
                 or x['bottleneck'] == 'tcptd_data' \
                 or x['bottleneck'] == 'tatcp_data' \
                 or x['bottleneck'] == 'tdsp_data' \
                 or x['bottleneck'] == 'tcctcr_data' \
                 or x['bottleneck'] == 'tcrtcc_data' \
                 or x['bottleneck'] == 'eatcc_data' \
                 or x['bottleneck'] == 'tccea_data':
                x['theory'] = round(x['theory']*x['vmem_workload'])
                x['unit'] = 'BPC'
            elif x['bottleneck'] == 'ldssp_read_data':
                x['theory'] = round(x['theory']*x['ds_workload'])
                x['unit'] = 'BPC'
            elif x['bottleneck'] == 'splds_idx':
                x['theory'] = round(x['theory']*x['sp_ds_workload'])
                x['unit'] = 'BPC'
            elif x['bottleneck'] == 'lds_latency':
                x['theory'] = round(x['lds_latency_vaule'])
                x['unit'] = 'CYCLE'
            elif "mmac" in x["name"]:
                x['theory'] = x['theory']*self.desc['threads/wave']*x['valu']*x['total_flops']*x['freq']/1024
                x['unit'] = 'TFLOPS'
            elif "fma_" in x["name"]:                        # Seems it is proper to only use Tflops or Tops for mmac and fma inst
                x['theory'] = x['theory']*self.desc['threads/wave']*x['valu']*x['total_flops']*x['freq']/1024
                x['unit'] = 'TFLOPS'
            elif x['bottleneck'] == 'sxgds_data':
                x['theory'] = 512*8/1024
                x['unit'] = 'bPC'
            elif x['bottleneck'] == 'gds_latency':
                x['theory'] = round(x['gds_latency_value'])
                x['unit'] = 'CYCLE'
            else:
                x['theory'] = x['theory']*self.desc['threads/wave']
                x['unit'] = 'TPC'
            return x
        #self.theo['theory'] = self.theo.apply(reunit, axis=1)
        #pdb.set_trace()        
        self.theo = self.theo.apply(reunit, axis=1)
        #self.theo.loc[:, ['theory','unit']] = self.theo.apply(reunit, axis=1)

        self.theo.dropna(axis = 1, how = "all", inplace = True)
        self.theo = self.theo.applymap(lambda x : round(x, 3) if type(x) != str else x )
        return self.theo.drop(self.inter_only_col, axis=1) #meta's updating will also in theo

    def cp_theory(self, vld):
        """CP Theory
        """
        d,m = self.desc,self.meta
        for i in vld:
            if i=='wpg':
                cp_dispatch_tg = 0
                cp_dispatch_latency = d['cp_dispatch_tg_payload']/d['cp_csdata_data_bw']
                #total_spis = d['se/core']*d['spi/se']
                ##CP dispatch TG to all SPIs in round-robin
                cp_traverse_all = d['cp_adc_prepare_tg']*d['cp_csdata_bus']
                #cp_dispatch_tg is the upper-limit value of dispatching
                if cp_traverse_all >= cp_dispatch_latency: #latency are hiding
                    cp_dispatch_tg = d['cp_adc_prepare_tg']
                else:
                    cp_dispatch_tg = cp_dispatch_latency #TODO: Valid it

                if("pip" in m.columns) and ("que" in m.columns) and ("gpd" in m.columns):
                    single_queue_or_not = (m['que'] == 1)
                    dispatch_latency_t          = m['que_send_delay'].apply(lambda x: d[x])
                    cp_dispatch_latency         = (m['pip'] * m['que'] - 1) * dispatch_latency_t + m["gpd"]  
                    self.theo.loc[~single_queue_or_not, 'dispatch_wave']    = m['pip'] * m['que'] * m["gpd"] * m['wpg'] / cp_dispatch_latency
                    self.theo.loc[single_queue_or_not, 'dispatch_wave']     = m['pip'] * m['wpg'] * cp_dispatch_tg
                else:
                    self.theo['dispatch_wave']  = m['wpg']*cp_dispatch_tg
                
                self.bottleneck_l.append('dispatch_wave')
            else:
                print("[NYI]cp_theory")
        
        return True

    def spi_theory(self, vld):
        """SPI Theory
        SPI is in charge of init user SGPR and VGPR and signaling SQ wave launched
        """
        d,m = self.desc,self.meta
        spis = d['spi/se'] * d['se/core']
        baton_internal = d["spi_use_baton"] * d['se/core']
        for i in vld: 
            if i == 'sgpr':
                m['sgpr_workload'] = m['sgpr']*d['bytes/sgpr']
                self.inter_only_col.append('sgpr_workload')
                #sdata bus is serial to all sq
                self.theo['init_sgpr'] = d['spi_sdata_bus']*d['spi_sdata_data_bw']*spis/m['sgpr_workload']
                self.bottleneck_l.append('init_sgpr')
            elif i == 'vgpr':
                m['vgpr_workload'] = m['vgpr']*d['bytes/vgpr']*d['threads/wave']    # unit is bytes/thread
                self.inter_only_col.append('vgpr_workload')

                #every thread has it's own vgpr
                self.theo['init_vgpr'] = d['spi_vdata_bus'] * d['spi_vdata_data_bw'] * spis / m['vgpr_workload']    # unit is thread/cycle
                self.bottleneck_l.append('init_vgpr')
            elif i == 'wave' and self.mode == 'WAVE':
                order_or_not = (m['unorder'] == 0)

                self.theo['alloc_wave_resource'] = d['spi_alloc_wave64']  * spis / m['wave']
                self.bottleneck_l.append('alloc_wave_resource')


                # in the ideal situation, a SE can deal a tg every 32 cycle set baton signal
                self.theo.loc[order_or_not, 'baton_limit'] = m["wpg"] / baton_internal * spis / m['wave'] # wave/cycle
                self.bottleneck_l.append('baton_limit')

                self.theo['spisq_cmd'] = d['spisq_bw'] * d['spisq_bus'] * spis / (m['wave'] * 206)
                self.bottleneck_l.append('spisq_cmd')
            else:
                print("[NYI]spi_theory")
        
        return True

    def sq_theory(self,vld):
        """SQ Theory
        """
        d,m = self.desc,self.meta
        sqs = d['sq/cu']*d['cu/se']*d['se/core']
        for i in vld:
            if i=='vmem':
                ################################
                # ID-EX pick rate in SQ internal
                # the pick rate in internal SQ internal from IB to EX pipeline
                #self.theo['sq_pick_vmem'] = d['sq_id_pick_vmem'] * sqs / m['vmem']
                #self.bottleneck_l.append('sq_pick_vmem')
                
                ################################
                # EX-FIFO issue rate in SQ internal
                # the issue rate in internal SQ internal from EX to FIFO pipeline
                soffset_or_not = (m['soffset'] == 1)
                self.theo.loc[soffset_or_not, 'cycle_in_ex']    = 4
                self.theo.loc[soffset_or_not, 'soffset_cycle']  = 4
                self.theo.loc[~soffset_or_not, 'cycle_in_ex']   = 1
                self.theo.loc[~soffset_or_not, 'soffset_cycle'] = 0
                
                #ex_fifo_issue_rate = sqs / cycle_in_ex # vmem inst/cycle
                self.theo['sq_ex_issue'] = sqs / self.theo['cycle_in_ex'] / m['vmem'] # wave/cycle
                self.bottleneck_l.append('sq_ex_issue')
                
                ################
                # SQ-SP-SIMD-SRC
                # only care d bus due to it always carry more workload and hence it is the slower bus, compared to the c bus
                # Besides, nothe that 1c requires a VGPR while 2c needs two VGPRs
                # 4 cycle used to get Soffset in EX. Note that for flat inst, d['soffset'] should be set as 0
                #XXX need to be explained by designer
                # for load case
                is_load = (m['vmemTYPE'] == 'load')
                component_is_not_zero = (m['component'] !=0)
                self.theo.loc[is_load & ~ component_is_not_zero, 'src_d_workload'] = (m['vmemPAY'])
                one_sq_sp_simd_src_rate = m['component']/d['sq_sp_src_simd_alloc']+self.theo['soffset_cycle']
                sq_sp_simd_src_rate = one_sq_sp_simd_src_rate.apply(lambda x: 0 if x == 0 else sqs/x)
                ##['vmem'] is inst/wave, so the final unit is wave/cycle
                self.theo.loc[component_is_not_zero & is_load, 'sqsp_simd_src_d'] = sq_sp_simd_src_rate / m['vmem']  
                self.bottleneck_l.append('sqsp_simd_src_d')

                is_store            = (m['vmemTYPE'] == 'store')
                component_is_one    = (m['component'] == 1)
                component_is_two    = (m['component'] == 2)
                store_dword_is_one  = (m['vmemPAY'] == 1)
                store_dword_is_two  = (m['vmemPAY'] == 2)
                store_dword_is_four = (m['vmemPAY'] == 4)
                self.theo.loc[is_store & ~component_is_not_zero, 'src_d_workload']                      = (m['vmemPAY'])
                self.theo.loc[is_store & store_dword_is_one & component_is_one, 'src_d_workload']       = 1
                self.theo.loc[is_store & store_dword_is_two & component_is_one, 'src_d_workload']       = 3
                self.theo.loc[is_store & store_dword_is_four & component_is_one, 'src_d_workload']      = 4
                self.theo.loc[is_store & store_dword_is_one & component_is_two, 'src_d_workload']       = 2
                self.theo.loc[is_store & store_dword_is_two & component_is_two, 'src_d_workload']       = 2
                self.theo.loc[is_store & store_dword_is_four & component_is_two, 'src_d_workload']      = 5

                one_sq_sp_simd_src_rate = self.theo['src_d_workload']/d['sq_sp_src_simd_alloc']+self.theo['soffset_cycle']
                sq_sp_simd_src_rate = one_sq_sp_simd_src_rate.apply(lambda x: 0 if x == 0 else sqs/x)
                ##['vmem'] is inst/wave, so the final unit is wave/cycle
                self.theo.loc[is_store, 'sqsp_simd_src_d'] = sq_sp_simd_src_rate / m['vmem']  
                self.bottleneck_l.append('sqsp_simd_src_d')
                
                self.theo.loc[is_store, 'src_c_workload']      = m['vmemPAY'] + m['component'] - self.theo['src_d_workload']
                one_sq_sp_simd_src_rate = self.theo['src_c_workload']/d['sq_sp_src_simd_alloc']+self.theo['soffset_cycle']
                sq_sp_simd_src_rate = one_sq_sp_simd_src_rate.apply(lambda x: 0 if x == 0 else sqs/x)
                ##['vmem'] is inst/wave, so the final unit is wave/cycle
                self.theo.loc[is_store, 'sqsp_simd_src_c'] = sq_sp_simd_src_rate / m['vmem']  
                self.bottleneck_l.append('sqsp_simd_src_c')

                ###########
                # SQ-TA-CMD
                sq_ta_single_inst_rate = d['cmd_bit/vmem'] / (d['sq_ta_cmd_bus'] * d['sq_ta_cmd_data_bw']) # cycles/inst
                #sq_ta_cmd_rate = sqs / (self.theo['soffset_cycle'] + sq_ta_single_inst_rate) # inst/cycle
                self.theo['sqta_cmd'] = sqs / (self.theo['soffset_cycle'] + sq_ta_single_inst_rate) / m['vmem'] # wave/cycle
                self.bottleneck_l.append('sqta_cmd')
            
            elif i=='branch':
                #[TODO]In most of shaders, the 'branch' part can be ignored unless they are testing target
                pass
        pass

    def sp_theory(self,vld): 
        """SP Theory
        """
        d,m = self.desc,self.meta
        sps = d['sp/cu']*d['cu/se']*d['se/core']
        simds = d['simd16/sp']*sps
        tpw = d['threads/wave']
        for i in vld:
            if i=='vop':
                def vop_theory(vop, d, simds):
                    vop_grp_l = vop.split('|') 
                    ptn = '([a-z0-9_]+)\*(\d+)'
                    vg_d = {}
                    for vg in vop_grp_l:
                        vname = re.sub(r'(\*\d+)\.0', '', vg)
                        sv_l = vg.split('-')
                        sval = 0
                        for sv in sv_l:
                            v_l = re.findall(r''+ptn+'', sv)
                            for v in v_l:
                                if '&' in sv:
                                    ##[TODO]No merging vop-s like co-exec currently, NYI
                                    ##More than one '&', like a&b&c should be also defined in desc
                                    #m = 0
                                    #sval += m
                                    pass
                                else:
                                    sval += d['simd_exec_'+v[0]]*simds/(int(v[1])*d['threads/wave'])
                        vg_d['sp_execI'+vname] = sval
                    return vg_d
                ##SE.apply() returns SE 'index {(vg_d)}'
                ##Use DF(dict()).T to create a DF has the same index as m and all columns are merged 
                ##automatically according with vnames
                vop_theo_df = DF(dict(m['vop'].apply(lambda x: vop_theory(x, d, simds)))).T
                self.theo = pd.concat([self.theo, vop_theo_df], axis=1)
                self.bottleneck_l.extend(list(vop_theo_df.columns))
            
            # for all of valu inst rate calc
            if i == 'vop32':
                try:
                    #[TODO] there are dependency check for two insts per loop
                    if "vrate2" in m.columns:
                        m["simd_exec_rate1"]    = m['vrate1'].apply(lambda x: d[x])
                        m["simd_exec_rate2"]    = m['vrate2'].apply(lambda x: d[x])
                        
                        # for now, multi wave with valus do not have round robin to hide latency
                        #multi_wave_or_not       = (m['wpg'] == 16)                                                  # multi wave could hide this wait latency
                        #m.loc[multi_wave_or_not, "wait_cycle_type"]     = 0
                        #m.loc[~multi_wave_or_not, "wait_cycle_type"]    = m['depend_type'].apply(lambda x: d[x])    # unit is Qcycle
                        
                        m["wait_cycle_type"]    = m['depend_type'].apply(lambda x: d[x])    # unit is Qcycle
                        m['inst_rate']          = 1 / ((tpw / m["simd_exec_rate1"] + tpw / m["simd_exec_rate2"] + m["wait_cycle_type"] * 4 * m['depend']) / 2)  # unit is inst/cycle/SIMD
                    #[TODO] there are only one inst per loop
                    else:
                        m["simd_exec_rate"]     = m['vrate'].apply(lambda x: d[x])
                        m['inst_rate']          = 1 / (tpw / m["simd_exec_rate"])           # unit is inst/cycle/SIMD
                except:
                    m['inst_rate'] = 1 / 4                                                  # use the peak rate for SQ->SP, unit is inst/cycle/SIMD
                
                self.theo['sp_exec'] = simds * m['inst_rate'] / m['vop32']                  # unit is wave/cycle
                self.bottleneck_l.append('sp_exec')

            #################
            # SP_TA_addr_rate
            if i=='component':
                # 2sps are connected with a ta in sh, so the number of ta is half of sps
                tas = d['ta/cu'] * d['cu/se'] * d['se/core']
                # # Byte/cycle
                sp_ta_addr_issue_rate = d['sp_ta_addr_data_bw'] * d['sp_ta_addr_bus'] * tas
                m['sta_workload'] = m['component'] * d['bytes/vgpr'] * d['threads/wave'] * m['vmem']
                self.inter_only_col.append('sta_workload')
                ## wave/cycle #For matrix opcode m['component'] is 0 thus SP_TA_addr is None
                #pdb.set_trace()
                self.theo['spta_addr'] = m['sta_workload'].apply(lambda x : np.nan if x== 0 else sp_ta_addr_issue_rate/x)
                self.bottleneck_l.append('spta_addr')
            
            #################
            # SP_TA_data_rate
            # ONLY for store inst
            if i=='vmemPAY':
                tas = d['ta/cu'] * d['cu/se'] * d['se/core']
                sp_ta_data_issue_rate = d['sp_ta_data_data_bw'] * d['sp_ta_data_bus'] * tas # Byte/cycle
                m['std_workload'] = m['vmemPAY'] * d['bytes/vgpr'] * d['threads/wave'] * m['vmem']
                self.inter_only_col.append('std_workload')
                store_or_not = (m['vmemTYPE'] == 'store')
                atomic_or_not = (m['vmemTYPE'] == 'atomic')
                self.theo.loc[store_or_not | atomic_or_not, 'spta_data'] = sp_ta_data_issue_rate / m['std_workload'] # wave/cycle
                self.bottleneck_l.append('spta_data')
        pass

    def lds_theory(self,vld): 
        """LDS Theory
        """
        d,m = self.desc,self.meta
        ldses = d['lds/cu']*d['cu/se']*d['se/core']

        for i in vld:
            if i=='cDS':
                #In current conflict test, the conflicted thread will occupy a single row with 
                #following addresses together until the next conflicting thread. 
                #E.g. tidig 0 and 16 are conflict threads, actually, 0-15 threads use addr 0 and 
                #16-31 use addr 128. So the size of instruction is not an issue here. E.g. 
                #under no conflict situation, one read2_b64 occupies 4DW, so for a w64, it will 
                #take 8 cycles. But under this conflicting scenario, it just take one cycles.
                #So how many cycles will be consumed only decided by conflicting numbers.
                ##How many cycles one wave needs when conflict = 1 on one inst
                conflict1_cycles = d['threads/wave']/d['lds_banks']
                self.theo['conflict_ds'] = ldses/(conflict1_cycles*m['cDS']*m['lds'])
                self.bottleneck_l.append('conflict_ds')

            if i == 'sp_ds_PAY':
                lds_sp_read_data_rate = d['sp_lds_idx_data_bw'] * d['sp_lds_idx_data_bus'] * ldses * 2         # Byte/cycle, per LDS connect 2 SPs with w buses
                self.theo['splds_idx'] = lds_sp_read_data_rate / m['sp_ds_workload']                                # wave/cycle

                self.theo.loc[(m['inst_type'] == 'ds_permute_b32') | (m['inst_type'] == 'ds_bpermute_b32'), 'splds_idx']  = self.theo['splds_idx'] * 0.667        # JIRA-KMPS-156
                self.theo.loc[(m['inst_type'] == 'ds_add_f32') , 'splds_idx']  = self.theo['splds_idx']/16
                self.bottleneck_l.append('splds_idx')

            if i == 'ds_PAY':
                lds_sp_read_data_rate = d['lds_sp_read_data_bw'] * d['lds_sp_read_data_bus'] * ldses * 2            # Byte/cycle
                self.theo['ldssp_read_data'] = lds_sp_read_data_rate / m['ds_workload']                             # wave/cycle
                self.bottleneck_l.append('ldssp_read_data')
        pass

    def lds_latency_theory(self,vld): 
        """LDS Theory
        """
        d,m = self.desc,self.meta
        ldses = d['lds/cu']*d['cu/se']*d['se/core']

        for i in vld:
            if i == 'lds_inst_type':
                m['lds_latency_vaule'] = m['lds_latency_inst'].replace(d)
                m['lds_latency_vaule'] = m['lds_latency_vaule'].astype(int)
                self.theo['lds_latency'] = m['lds_latency_vaule']/10000       ##latency case, need a little vaule to make btnk=lds_latency. 
                self.theo['lds_latency_vaule'] = m['lds_latency_vaule']
                self.bottleneck_l.append('lds_latency')
        pass
    
    def ta_theory(self,vld):
        """TA theory
        """
        d, m = self.desc, self.meta
        tas = d['ta/cu'] * d['cu/se'] * d['se/core']
        
        #################
        # TA_TCP_cmd_rate
        # In Bowen A0, the cmd rate of ta to tc if fixed
        ta_tc_single_inst_rate = d['cmd_bit/vmem'] / (d['ta_tc_cmd_bus'] * d['ta_tc_cmd_data_bw']) # cycles per inst
        self.theo['tatcp_cmd'] = tas / ta_tc_single_inst_rate / m['vmem'] # wave/cycle
        self.bottleneck_l.append('tatcp_cmd')

        
        ##################
        # TA_TCP_addr_rate
        if 'vmemCOA' in vld:
            total_vmem_thread = d['threads/wave'] * m['vmem'] # thread per wave
            coal_or_not = (m['vmemCOA'] == 'coalesced')
            
            # for coal with comp or not and dw num
            self.theo.loc[coal_or_not & (m['component'] == 1) & (m['vmemPAY'] == 1), 'tatcp_addr']             = tas * 16 / total_vmem_thread      # default is None
            self.theo.loc[coal_or_not & (m['component'] == 2) & (m['vmemPAY'] == 1), 'tatcp_addr']             = tas * 8 / total_vmem_thread       # default is None
            self.theo.loc[coal_or_not & (m['component'] == 1) & (m['vmemPAY'] == 2), 'tatcp_addr']             = tas * 8 / total_vmem_thread       # default is None
            self.theo.loc[coal_or_not & (m['vmemPAY'].isin([3, 4])), 'tatcp_addr']                             = tas * 4 / total_vmem_thread       # default is None
            
            # for uncoal with comp or not and dw num
            self.theo.loc[~coal_or_not & (m['component'] == 1) & (m['vmemPAY'] == 1), 'tatcp_addr']            = tas * 4 / total_vmem_thread       # default is None
            self.theo.loc[~coal_or_not & (m['component'] == 2) & (m['vmemPAY'] == 1), 'tatcp_addr']            = tas * 2 / total_vmem_thread       # default is None
            self.theo.loc[~coal_or_not & (m['component'] == 2) & (m['vmemPAY'] == 2), 'tatcp_addr']            = tas * 4 / total_vmem_thread       # default is None
            
            # flat_scratch is different from buffer_global inst
            if 'flat_scratch' in m.columns:
                self.theo.loc[~coal_or_not & (m['flat_scratch'] == 1) & (m['component'] == 1) & (m['vmemPAY'] == 2), 'tatcp_addr']      = tas * 4 / total_vmem_thread   # double rate for this scenario
            else:
                self.theo.loc[~coal_or_not & (m['component'] == 1) & (m['vmemPAY'] == 2), 'tatcp_addr']        = tas * 2 / total_vmem_thread       # default is None
            self.theo.loc[~coal_or_not & (m['vmemPAY'].isin([3, 4])), 'tatcp_addr']                            = tas * 4 / total_vmem_thread       # default is None
            self.bottleneck_l.append('tatcp_addr')
        else:
            pass

        ##################
        # TA_TCP_data_rate
        ta_tcp_data_rate = d['ta_tcp_data_data_bw'] * d['ta_tcp_data_bus'] * tas # Byte/cycle
        store_or_not = (m['vmemTYPE'] == 'store') 
        atomic_or_not = (m['vmemTYPE'] == 'atomic')
        self.theo.loc[store_or_not | atomic_or_not, 'tatcp_data'] = ta_tcp_data_rate / m['vmem_workload'] # wave/cycle
        self.bottleneck_l.append('tatcp_data')
        
        #######################################
        #TODO maybe need a theory from TA ot TD

    def tcp_theory(self, vld): 
        #[TODO]How TCP dealing received address
        d, m = self.desc, self.meta
        tcps = d['tcp/cu'] * d['cu/se'] * d['se/core']
        
        if 'vmemCAC' in vld:
            hit_tcp_or_not = (m['vmemCAC'] == 'TCP')
            load_or_not = (m['vmemTYPE'] == 'load')
            store_or_not = (m['vmemTYPE'] == 'store')
            atomic_or_not = (m['vmemTYPE'] == 'atomic')
            coal_or_not = (m['vmemCOA'] == 'coalesced')

            ##################
            # TCP_TCR_req_rate
            ##TODO: set 128B request or 64B request from meta. Since 128B request spends 2 cycles 
            ##that equals 2 continuous 64B requests, so we can just use 64B_req here to calculate
            #pdb.set_trace()
            self.theo['tcptcr_req'] = 64 * d['tcp_tcr_64byte_req'] * tcps / m['vmem_workload'] # wave/cycle
            self.bottleneck_l.append('tcptcr_req')

            #######################
            # TCR_TCP_ret_data_rate

            tcr_tcp_ret_data_rate = d['tcr_tcp_ret_data_data_bw'] * d['tcr_tcp_ret_data_bus'] * tcps # Byte/cycle
            self.theo.loc[~hit_tcp_or_not & load_or_not & coal_or_not, 'tcrtcp_data'] = tcr_tcp_ret_data_rate / m['vmem_workload'] # wave/cycle
            self.theo.loc[~hit_tcp_or_not & (load_or_not | atomic_or_not) & ~coal_or_not, 'tcrtcp_data'] = tcr_tcp_ret_data_rate * 0.5 / m['vmem_workload']    # For uncoal the tcr_tcp_ret_data is 64B
            self.bottleneck_l.append('tcrtcp_data')
            
            ########################
            # TCP_TCR_hole_data_rate
            tcp_tcr_hole_data_rate = d['tcp_tcr_hole_data_data_bw'] * d['tcp_tcr_hole_data_bus'] * tcps # Byte/cycle
            self.theo.loc[~hit_tcp_or_not & store_or_not, 'tcptcr_hdata'] = tcp_tcr_hole_data_rate / m['vmem_workload'] # wave/cycle
            self.bottleneck_l.append('tcptcr_hdata')
        else:
            pass
        
        ##################
        # TCP_TD_data_rate
        # it may be aligned with TA-TCP-addr rate
        # ONLY for load inst
        load_or_not = (m['vmemTYPE'] == 'load')
        atomic_or_not = (m['vmemTYPE'] == 'atomic')
        coal_or_not = (m['vmemCOA'] == 'coalesced')
        dword_or_not = (m['vmemPAY'] == 1)
        dwordx2_or_not = (m['vmemPAY'] == 2)
        dwordx4_or_not = (m['vmemPAY'] == 4)
        tcp_td_data_rate = tcps * d['tcp_td_data_bus'] * d['tcp_td_data_data_bw'] # Byte/cycle

        # the rate is given by TD spec
        # for coal
        #self.theo.loc[load_or_not & coal_or_not & (m['component'] == 1), 'tcptd_data'] = tcp_td_data_rate / m['vmem_workload'] # wave/cycle
        #self.theo.loc[load_or_not & coal_or_not & dwordx4_or_not & (m['component'] == 2), 'tcptd_data'] = tcp_td_data_rate / m['vmem_workload']
        
        self.theo.loc[load_or_not & coal_or_not & (m['component'] == 1), 'tcptd_data'] = tcp_td_data_rate / m['vmem_workload']        # For DWx1/2/4 coal and c=1
        self.theo.loc[load_or_not & coal_or_not & ~dwordx4_or_not & (m['component'] == 2), 'tcptd_data'] = tcp_td_data_rate * 0.5 / m['vmem_workload']    #For DWx1/2 coal and c = 2
        self.theo.loc[load_or_not & coal_or_not & dwordx4_or_not & (m['component'] == 2), 'tcptd_data'] = tcp_td_data_rate / m['vmem_workload']   #For DWx4 coal and c = 2
        self.theo.loc[load_or_not & coal_or_not & dwordx4_or_not & (m['component'] == 0), 'tcptd_data'] = tcp_td_data_rate / m['vmem_workload']   #For DWx4 coal and c = 0(matrix_load)
        
       
 # wave/cycle
        # [TODO] the below value seems not correct, the tcp_td_data_rate result in simulation is faster than the speed given in spec
        # it need to be confirmed from Taoran
        # for DWX4 buffer load, coal cannot improve the rate
        #self.theo.loc[load_or_not & coal_or_not & ~dwordx4_or_not & (m['component'] == 2), 'tcptd_data'] = tcp_td_data_rate * 0.5 / m['vmem_workload'] # wave/cycle
        
        # for uncoal: flat_scratch is different from buffer_global inst
        if 'flat_scratch' in m.columns:
            self.theo.loc[(load_or_not | atomic_or_not) & ~coal_or_not & (m['flat_scratch'] == 1) & ~dwordx4_or_not & (m['component'] == 1), 'tcptd_data'] = tcp_td_data_rate * 0.5 / m['vmem_workload']
        else:
            self.theo.loc[(load_or_not | atomic_or_not) & ~coal_or_not & ~dwordx4_or_not & (m['component'] == 1), 'tcptd_data'] = tcp_td_data_rate * 0.25 / m['vmem_workload'] # For DWx1/2 uncoal and c =1 
        self.theo.loc[(load_or_not | atomic_or_not) & ~coal_or_not & dword_or_not & (m['component'] == 2), 'tcptd_data'] = tcp_td_data_rate * 0.125 / m['vmem_workload']   # For DWx1 uncoal and c = 2
        self.theo.loc[(load_or_not | atomic_or_not) & ~coal_or_not & dwordx2_or_not & (m['component'] == 2), 'tcptd_data'] = tcp_td_data_rate * 0.5 / m['vmem_workload']   # For DWx2 uncoal and c = 2
        self.theo.loc[(load_or_not | atomic_or_not) & ~coal_or_not & dwordx4_or_not, 'tcptd_data'] = tcp_td_data_rate / m['vmem_workload']          # For DWx4 uncoal and c = 0(matrix_load)/1/2
        self.bottleneck_l.append('tcptd_data')
    
    """
    def tc_theory(self,vld):
        d, m = self.desc, self.meta

        # coalesce or not
        if 'vmemCOA' in vld:
            m['coa'] = m['vmemCOA']
            self.inter_only_col.append('coa')
        # LDS or VGPR as the dst
        if 'vmemTER' in vld:
            m['compN'] = m['vmemTER'].apply(lambda x: 1 if x=='lds' else None)
            self.inter_only_col.append('compN')
        
        if 'vmemPAY' in vld and 'vmemCAC' in vld:

            # confunse for the meaning of m['dataF']        
            m['dataF'] = m['vmemPAY']/m['vmem'] # [DW * wave / thread / inst] 
            self.inter_only_col.append('dataF')

            # workload, unit is Byte per inst
            m['waveB'] = m['vmemPAY'].apply(lambda x: x*d['threads/wave']*DW2B)
            self.inter_only_col.append('waveB')
            
            # hit or not, hit target-TCP, TCC or MEM, hite rate
            def parse_cac(req, cac):
                type, target, rate = re.search(r'(hit|miss)([A-Z]+)(\d+)?', cac).groups()
                if type == 'hit':
                    return target == req and rate == None
            
            # To use the hit rate to calc the results
            m['tcpB'] = m['vmemCAC'].apply(lambda x: parse_cac('TCP', x))*m['waveB']
            self.inter_only_col.append('tcpB')
            m['tccB'] = m['vmemCAC'].apply(lambda x: parse_cac('TCC', x))*m['waveB']
            self.inter_only_col.append('tccB')
        else:
            print('vmemPAY and vmemCAC must exist in meta together')
            sys.exit()

        coalesced = m['coa'].apply(lambda x: 1 if x=='coalesced' else 0)
        tas = d['ta/cu']*d['cu/se']*d['se/core']
        sp_ta_addr_bw_per_sp = d['sp_ta_addr_bus']*d['sp_ta_addr_addr_bw']
        ta_tcp_data_bw_per_core = tas*d['ta_tcp_data_bus']*d['ta_tcp_data_bus_bw']
        ##if coalesced, how fast ta can coalescing the address of buffer command depending on 
        ##sp-ta-addr-bw and the dataF and compN of a instruction.
        def cal_sp_ta_addr_perf(coa, compN, dataF, vmem):
            tas = d['ta/cu']*d['cu/se']*d['se/core']
            data_per_req_coa = compN*dataF*DW2B
            total_reqs = vmem*d['threads/wave'] # inst * thread / wave^2
            if coa=='coalesced':
                return tas*sp_ta_addr_bw_per_sp/float(total_reqs*data_per_req_coa)
        m['spta_addr'] = m.T.apply(lambda x: cal_sp_ta_addr_perf(x['coa'], x['compN'], x['dataF'], x['vmem']))
        self.theo['spta_addr'] = m['spta_addr']
        self.bottleneck_l.append('spta_addr')
        ##Under coalesced, the taOUT has the same capability as spta_addr
        m['tatc_addr'] = m['spta_addr']*coalesced
        self.theo['tatc_addr'] = m['tatc_addr']
        self.bottleneck_l.append('tatc_addr')
        
        #The 'hit' implies 100% hit for every wave. Under this circumstance, the test should control requests in one wave always hit in target. 
        #[XXX]To calculate ratio of data payload of a threads bundle in per-core cache is more like a no-need-to-be-concerned mark since even there is a test designed like have countless buffer requests and per-wave calculation tells that the total size of it exceeds the per-core-tcp/tcc, actually it means nothing because those requests is not sent down in one time. 
        #Considering this situation, the 'alloc_tcp' is actually becoming one confusing present and should be commented out. 
        #tcp_size_per_core = d['tcp_tagrams']*d['tcp_cachelines_per_tagram']*d['tcp_cacheline_size']*d['cu/se']*d['se/core']
        #m['alloc_tcp'] = tcp_size_per_core/m['tcpB']
        #self.theo['hit_tcp'] = m['alloc_tcp']
        #self.bottleneck_l.append('hit_tcp')
    """

    def td_theory(self, vld): 
        d, m = self.desc, self.meta
        tds = d['td/cu'] * d['cu/se'] * d['se/core']
        
        ##################
        # TD_SP_data_rate
        # it may be aligned with TA-TCP-addr rate
        td_sp_data_rate = tds * d['td_sp_data_bus'] * d['td_sp_data_data_bw'] # Byte/cycle
        load_or_not = (m['vmemTYPE'] == 'load')
        atomic_or_not = (m['vmemTYPE'] == 'atomic')
        dword_or_not = (m['vmemPAY'] == 1)
        
        # the rate is given by TD spec for buffer or flat inst
        self.theo.loc[(load_or_not | atomic_or_not) & dword_or_not & (m['component'] == 2), 'tdsp_data'] = td_sp_data_rate * 0.5 / m['vmem_workload']           # For DWx1 c =2 and coal/uncoal
        self.theo.loc[(load_or_not | atomic_or_not) & ~dword_or_not & (m['component'] != 0), 'tdsp_data'] = td_sp_data_rate / m['vmem_workload']                # For DW2/4 c=1/2 and coal/uncoal
        self.theo.loc[(load_or_not | atomic_or_not) & dword_or_not & (m['component'] == 1 ), 'tdsp_data'] = td_sp_data_rate / m['vmem_workload']                # For DWx1 c=1 and coal/uncoal
        
        # ONLY for matrix copy inst
        if (('vmemSW' in m.columns) & ('vmemBPE' in m.columns)):
            dwordx4_or_not = (m['vmemPAY'] == 4)
            ppbuffer_or_not = (((m['vmemTER'] == 'lds') & (m['vmemBPE'] == 8) & (m['vmemSW'] == 'ON')) | ((m['vmemTER'] == 'vgpr') & (m['vmemBPE'] == 16) & (m['vmemSW'] == 'ON')))
            self.theo.loc[load_or_not & dwordx4_or_not & (m['component'] == 0) & ~ppbuffer_or_not, 'tdsp_data'] = td_sp_data_rate / m['vmem_workload']       # For Matrix_load_* which spend 16 cycle to send a instruction data(1024B)
            self.theo.loc[load_or_not & dwordx4_or_not & (m['component'] == 0) & ppbuffer_or_not, 'tdsp_data'] = td_sp_data_rate * 0.5 / m['vmem_workload']  # For Matrix_load_* which spend 32cycle to send a instruction data(1024B)
        else:
            pass

        self.bottleneck_l.append('tdsp_data')

    def tcc_theory(self,vld): 
        """TCC Theory
        """
        d,m = self.desc,self.meta
        tccs = d['tcc_bank']

        for i in vld:
            if i == 'vmemTYPE':
                load_or_not = (m['vmemTYPE'] == 'load')
                atomic_or_not = (m['vmemTYPE'] == 'atomic')
                store_or_not = (m['vmemTYPE'] == 'store')
                hit_tcp_or_not = (m['vmemCAC'] == 'TCP')
                coal_or_not = (m['vmemCOA'] == 'coalesced')
                
                tcc_tcr_read_rate = d['tcc_tcr_rdata_data_bw'] * d['tcc_tcr_rdata_bus'] * tccs    # Byte/cycle

                if "coaRATIO" in m.columns:
                    self.theo.loc[load_or_not & coal_or_not & ~hit_tcp_or_not, 'tcctcr_data'] = tcc_tcr_read_rate * m['coaRATIO'] / m['vmem_workload']  # wave/cycle
                else:
                    self.theo.loc[load_or_not & coal_or_not & ~hit_tcp_or_not, 'tcctcr_data'] = tcc_tcr_read_rate / m['vmem_workload']
                
                self.theo.loc[load_or_not & ~coal_or_not & ~hit_tcp_or_not, 'tcctcr_data'] = tcc_tcr_read_rate * 0.5 / m['vmem_workload']                                   # wave/cycle
                self.theo.loc[atomic_or_not, 'tcctcr_data'] = tcc_tcr_read_rate * 0.5 / m['vmem_workload'] / 3                                                              # wave/cycle
                
                self.bottleneck_l.append('tcctcr_data')
                
                tcc_write_rate = d['tcr_tcc_wdata_data_bw'] * d['tcr_tcc_wdata_bus'] * tccs # Byte/cycle
                self.theo.loc[(store_or_not | atomic_or_not) & ~hit_tcp_or_not, 'tcrtcc_data'] = tcc_write_rate / m['vmem_workload'] # wave/cycle
                self.bottleneck_l.append('tcrtcc_data')
            elif i == 'vmemCAC':
                hit_mem_or_not = (m['vmemCAC'] == 'MEM')
                load_or_not = (m['vmemTYPE'] == 'load')
                store_or_not = (m['vmemTYPE'] == 'store')
                
                ea_tcc_rdret_rate = d['ea_tcc_rdret_data_bw'] * d['ea_tcc_rdret_bus'] * tccs # Byte/cycle
                self.theo.loc[hit_mem_or_not & load_or_not, 'eatcc_data'] = ea_tcc_rdret_rate / m['vmem_workload'] # wave/cycle
                self.bottleneck_l.append('eatcc_data')
                
                tcc_ea_wrret_rate = d['tcc_ea_wrret_data_bw'] * d['tcc_ea_wrret_bus'] * tccs # Byte/cycle
                self.theo.loc[hit_mem_or_not & store_or_not, 'tccea_data'] = tcc_ea_wrret_rate / m['vmem_workload'] # wave/cycle
                self.bottleneck_l.append('tccea_data')
            else:
                pass

    def gds_theory(self, vld):
        """GDS Theory
        """
        d, m = self.desc, self.meta
        for i in vld: 
            if i == 'gds_wpg':
                self.theo['sxgds_data'] = 512
                self.bottleneck_l.append('sxgds_data')
        return True
    
    def gds_latency_theory(self, vld):
        '''GDS latency theory
        '''
        d, m = self.desc, self.meta
        for i in vld:
            if i == 'gds_inst_type':
                m['gds_latency_value'] = m['gds_latency_inst'].replace(d)
                m['gds_latency_value'] = m['gds_latency_value'].astype(int)
                self.theo['gds_latency'] = m['gds_latency_value'] / 10000 # gds cycle unit 10ns to 1us
                self.theo['gds_latency_value'] = m['gds_latency_value']
                self.bottleneck_l.append('gds_latency')
        pass

    def ea_theory(self,vld):
        pass
    
    def mem_theory(self,vld):
        pass

if __name__=='__main__':
    pass

