#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buffer load (To LDS) Performance Model
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

dv_dir = cdir + '/../../cache/'
testpm_cfg_d = {
    'structure_buffer' : {
        'dv'            : dv_dir + 'perf_structure_buffer.dv'
        ,'test_ptn'     : "perf_structure_buffer_([a-z]+)_dwordx(\d)_hit([A-Z]+)_S(\d+(\.\d+)?)K_N(\d+)_B(\d+)_CSW([a-z]+)"
        ,'test_param_l' : ['vmemTYPE', 'vmemPAY', 'vmemCAC', 'stride', 'n128', 'bpi', 'csw']  # , 'stride', 'csw'
        ,'warmup'       : 2
    }
}

class StructureBufferPM(PerfTestPM):

    def __init__(self):
        # call the __init__ func of parent class
        super(StructureBufferPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['structure_buffer']

    def theory(self, desc, test = None, gui_en = False, **kw):
        """
        Buffer Load (To LDS) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        super().theory(desc, test, gui_en, **kw)
       
        meta_col = ['name',
                    'wpg',                                          # for cp theory
                    'vgpr', 'sgpr', 'unorder',                      # for spi theory
                    'valu', 'salu', 'vmem', 'smem', 'soffset',      # for sq theory 
                    'vop32', 'component', 'vmemPAY',                # for sp theory
                    'vmemCOA',                                      # for ta theory
                    'vmemTER',                                      # for td theory
                    'vmemCAC',                                      # for tcp theory
                    'stride',                                       # for tcp theory
                    'n128',                                         # for tcp theory
                    'bpi',                                          # for tcp theory
                    'csw',                                          # for tcp theory
                    'vmemTYPE'                                      # for tcc theory
                    ]
        
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(self.test_info_df.loc[:,meta_col], columns = meta_col)
       
        hit = meta_df['name'].apply(lambda x: 
                'TCP' if (re.match("perf_structure_buffer_([a-z]+)_dwordx(\d)_hitTCP_\w+", x)) else 'TCC')
        #print('hit:',hit)
        if hit[0]=='TCP':
            rdir = kw.get('rdir', None)
            # for ooo test, we only use the algo-spisq_launch_done_ave to get the performance results
            algo = 'spisq_launch_done_ave'
            
            # use below test as the reference test
            #test_off = 'perf_buffer_instruction_ls_ooo_OFF'
            test_off = test.replace("on", "off")
            self.measure(desc, algo, rdir, test_off, gui_en = False, **kw)
            
            self.theo = self.meas
            self.theo['bottleneck'] = 'wavelifetime'    # unit is cycle per wave
            theo_clumns = ['name', 'measure', 'bottleneck', 'unit']
            self.theo = pd.DataFrame(self.theo, columns = theo_clumns)
            self.theo.rename(columns = {'measure': 'theory'}, inplace = True)
            self.theo['name'] = test
            self.meas = DF() #Clean out reference test result for check()

            if gui_en:
                gui = util.PMGui()
                gui.run([self.theo])

            return self.theo
        else:
            ################
            ## cp setting###
            # get meta_df['wgp'] by testname with test_info_df
            ## cp setting###
            ################

            #################
            ## spi setting###
            meta_df['vgpr']  = 1            # thread_id in V0 is needed to control addr
            meta_df['sgpr']  = 3            # S0 & S1 for get the buffer addr and S2 gets the threadgroup id
            meta_df['unorder'] = 1          # do not use baton
            ## spi setting###
            #################
            
            #################
            ## sq setting####
            meta_df['salu']  = 3            # for buffer load dw, it shoud be 3 at less.
            meta_df['valu']  = 8            # for buffer load dw, it shoud be 8 at less.
            meta_df['smem']  = 1
            meta_df['soffset'] = 0          # for now, we just use buffer inst with Soffset
            
            # get meta_df['vmem'] by testname with test_info_df
            ## sq setting####
            meta_df['vmem'] = 32/meta_df['vmemPAY']  # dwpi=1/2/4 -> ipw=32/16/8
            #################

            #################
            ## sp setting####
            meta_df['vop32'] = meta_df['valu']  # for sp using, instead of sq issuing
            # get meta_df['vmemPAY'] by testname with test_info_df
            # get meta_df['component'] by testname with test_info_df
            ## sp setting####
            #################
            
            #################
            ## ta setting####
            #meta_df['vmemCOA'] = meta_df['name'].apply(lambda x: 
            #    'uncoalesced' if (re.match("perf_structure_buffer_([a-z]+)_dwordx(\d)_hit([A-Z]+)_S(\d+(\.\d+)?)K_N(\d+)_B64_\w+", x)) else 'coalesced')
            #meta_df['vmemCOA'] = meta_df['name'].apply(lambda x: 
            #    'uncoalesced' if (meta_df['bpi'] == '64') else 'coalesced')
            meta_df['vmemCOA'] = 'coalesced'
            def serach_keywoard(test):
                align_pattern = r'B(\d+)'
                match = re.search(align_pattern,test)
                if match:
                    return match.group(1)
            meta_df['coaRATIO'] = meta_df['name'].apply(lambda x: 
                serach_keywoard(x))

            def judge_ratio(align,dwordx):
                if align == 128 and dwordx != 2:  # component=2 when structure buffer, thus TA cannot coalesce, tcp cannot merge 128B
                    return 1
                else:
                    return 0.5
                #elif dwordx == 2:     
                #    return 0.5
                #elif align == 64:            
                #    return 0.667
                #elif 0<align and align<64 and dwordx == 1:            
                #    return 0.625
                #elif 0<align and align<64 and dwordx == 4:            
                #    return 0.654
                #elif 64<align and align<128 and dwordx == 1:            
                #    return 0.625
                #elif 64<align and align<128 and dwordx == 4: 
                #    return 0.531
            def judge_coa(align,dwordx):
                if align == 128:
                    return 'coalesced'
                elif dwordx == 2:     
                    return 'uncoalesced' #must & component==2, TODO, maybe TA and TC coa are not same
                    #return 'coalesced'
                else:     
                    return 'coalesced'
            for index, row in meta_df.iterrows():
                meta_df.loc[index,'coaRATIO'] = judge_ratio(int(row['coaRATIO']),int(row['vmemPAY']))
                meta_df.loc[index,'vmemCOA'] = judge_coa(int(row['coaRATIO']),int(row['vmemPAY']))

            ## ta setting####
            #################

            #################
            ## td setting####
            meta_df['vmemTER'] = 'vgpr'      # lds or vgpr, for this case, lds is selected
            ## td setting####
            ################# 
            
            ##################
            ## tcp setting####
            # get meta_df['vmemPAY'] by testname with test_info_df
            # get meta_df['vmemCAC'] by testname with test_info_df
            meta_df['component'] = 2 
            #meta_df['vmemCAC'] = 'TCP' 
            meta_df['wpg'] = 4 
            ## tcp setting####
            ##################

            ##################
            ## tcc setting####
            # get meta_df['vmemTYPE'] by testname with test_info_df
            ## tcc setting####
            ##################
            
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
        super().check(desc, edir, test, **kw)
        self.chk_df['check'] = self.chk_df.T.apply(lambda x : 'pass' if x['name'].endswith('off') else x['check'])
        if gui_en:
            gui = util.PMGui()
            gui.run([self.chk_df])
        return self.chk_df
      

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = StructureBufferPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en, rdir=opt.rdir)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

