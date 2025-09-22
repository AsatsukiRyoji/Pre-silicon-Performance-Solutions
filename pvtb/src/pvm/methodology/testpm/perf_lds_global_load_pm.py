#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global load (To LDS) Performance Model
@author: Ma Xingxing
"""
import os,sys,re
from pandas import DataFrame as DF
import pandas as pd
import pdb

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir + '../')

import utility.util as util

from theory.core_performance_theory import ComputeCoreTheory as CCT
from measure.core_performance_measure import ComputeCoreMeasure as CCM
from check.core_performance_check import ComputeCoreCheck as CCC

class GlobalLoadLdsPM:
    
    def __init__(self):
        self.theo, self.meas, self.chk = DF(), DF(), DF()
        #self.log = util.PMLog(name = 'perf_lds_global_load_pm', path = cdir)
        pass

    @staticmethod  # create a func that can be called directly by the class name, instead of the instance name
    def acquire_all_tests(test = None, type = 'theory'):
        """Common function to acquire all tests
        :test: list or None
        """
        
        # abs dir is required
        dv = cdir + '../../cache/perf_lds_global_load.dv'
        test_ptn = "perf_lds_global_([a-z]+)_dwordx(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)"

        # ipw is vmem-instruction per wave
        test_param_l = ['vmemTYPE', 'vmemPAY', 'vmemCAC', 'vmem', 'wpg']
        
        test_info_df = util.conv2df(util.get_test_desc(dv, test_ptn, test_param_l))

        if test != None:  
            test_info_df = (test_info_df.set_index(test_info_df['name'])).loc[test,:]
            
            # reset index to serial number
            test_info_df.reset_index(drop = True, inplace = True)

        if type == 'measure':
            return DF(test_info_df['name'])
        
        else:
            return test_info_df

    def theory(self, desc, test = None, **kw):
        """Global Load (To LDS) Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """

        if type(test) == str:
            try:    test = eval(test)               # If it's a str([])
            except: test = [test]
        
        test_info_df = GlobalLoadLdsPM.acquire_all_tests(test)
        
        meta_col = ['name', 'wpg', 'vgpr', 'sgpr', 'valu', 'salu', 'vmem', 'smem', 
                    'vop32', 'vmemPAY', 'vmemCAC', 'vmemTYPE']
        
        # Unit is per wave
        meta_df = DF(test_info_df.loc[:,meta_col], columns = meta_col)
        
        ################
        ## cp setting###
        # get meta_df['wgp'] by testname with test_info_df
        ## cp setting###
        ################
        

        #################
        ## spi setting###
        meta_df['vgpr']  = 1            # thread_id in V0 is needed to control addr
        meta_df['sgpr']  = 3            # S0 & S1 for get the buffer addr and S2 gets the threadgroup id
        ## spi setting###
        #################
        
        #################
        ## sq setting####
        meta_df['salu']  = 1            # for global load dw, it shoud be 3 at less.
        meta_df['valu']  = 10            # for global load dw, it shoud be 8 at less.
        meta_df['smem']  = 1
        meta_df['soffset'] = 0          # For global opcode the value of soffset is 0
        
        # get meta_df['vmem'] by testname with test_info_df
        ## sq setting####
        #################

        #################
        ## sp setting####
        meta_df['vop32'] = meta_df['valu']
        # get meta_df['vmemPAY'] by testname with test_info_df
        meta_df['component'] = 1
        ## sp setting####
        #################
        
        #################
        ## ta setting####
        meta_df['vmemCOA'] = 'coalesced'
        ## ta setting####
        #################
        
        ##################
        ## tcp setting####
        # get meta_df['vmemPAY'] by testname with test_info_df
        # get meta_df['vmemCAC'] by testname with test_info_df
        ## tcp setting####
        ##################

        ##################
        ## tcc setting####
        # get meta_df['vmemTYPE'] by testname with test_info_df
        ## tcc setting####
        ##################
        """
        # [TODO]Passing missing labels to .loc will be deprecated, fix it at then
        # Unit is per wave
        meta_df = DF(test_info_df.loc[:,meta_col], columns = meta_col)
        meta_df['vgpr']  = 1            # thread_id in V0 is needed to control addr
        meta_df['sgpr']  = 3            # S0 & S1 for get the buffer addr and S2 gets the threadgroup id
        meta_df['salu']  = 99           # [TODO] templarily use a max value of all buffer load test due to salu issue is not the bottelneck
        meta_df['valu']  = 105          # [TODO] templarily use a max value of all buffer load test due to valu issue is not the bottelneck

        meta_df['vop32'] = meta_df['valu']

        #vmem
        meta_df['vmemTER'] = 'lds'      # [FIXME] Wrong value, and should be vgpr, but meet error if so
        meta_df['vmemPAY'] = meta_df['vmemPAY'].apply(lambda x: 1 if pd.isnull(x) else x)
        meta_df['vmemPAY'] = meta_df['vmem'] * meta_df['vmemPAY']

        # s_load_dwordx4 load constant from memory to SQC, the test uses warm-up waves to assure 
        # it's already loaded. So only the issue(from sq to sqc) of it is calculated
        meta_df['smem']  = 1
        """
        cct = CCT(desc, meta_df)
        self.theo = cct.get_theory()
        self.theo.dropna(axis = 1, how = "all", inplace = True)
        gui = util.PMGui()
        gui.run([self.theo])
        #print(self.theo)
        return self.theo
    
    def measure(self, desc, edir = './', test = None, **kw):
        """GLOBAL Load (To VGPR) PM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """
        if type(test) == str:
            try:    test = eval(test)           #If it's a str([])
            except: test= [test]

        algo_l = ['tcctcr_rdata_muu','tdsp_data_muu']
        
        # Just keep the first one to compare with theory to simplify dealing
        if kw.get('check_request'): algo_l = [algo_l[0]]    
        
        meta_df = GlobalLoadLdsPM.acquire_all_tests(test, 'measure')
        meta_df['edir'] = meta_df['name'].apply(lambda x: edir + x + '/')
        ##remove invalid out directory is generated by test.dv
        meta_df['edir'] = meta_df['edir'].apply(lambda x: x if os.path.isdir(x) else None)
        meta_df.dropna(inplace = True)
        meta_df['warmup'] = 1
        meta_df['algo'] = ','.join(algo_l)
        ccm = CCM(desc, meta_df)
        _df = ccm.get_measure()
        _df = _df.drop(['edir', 'warmup'], axis = 1)
        out = [DF()]
        _df.T.apply(util.split_se_2df, args=(',', out)) 
        self.meas = out[0]
        print(self.meas)
        return self.meas

    def check(self, desc, edir, test, **kw):
        '''
        :test: str or list. 
        '''
        if type(test) == str:
            try:    test = eval(test)           # If it's a str([])
            except: test = [test]
        
        meth_desc = util.get_cfg_f(cdir + '../methodology.cfg')

        #chk_df = DF(columns=meth_desc['test_check_col'].split(','))
        
        self.theory(desc, test)
        self.measure(desc, edir, test, check_request = True)
        chk_df = self.theo.reindex(columns = meth_desc['test_check_col'].split(','))

        # [XXX]The 'name' is updated again here per the same list, if the test output
        # couldn't be found under edir, the value becomes 'TBD'
        chk_df.update(self.meas) 
        ccc = CCC(desc, chk_df)
        chk_df = ccc.get_chk()
        self.chk_df = chk_df
        
        #gui = util.PMGui()
        #gui.run([chk_df])
        
        return self.chk_df

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = GlobalLoadLdsPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.edir, opt.test)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test)
    else:
        print('NYI')
        sys.exit()

