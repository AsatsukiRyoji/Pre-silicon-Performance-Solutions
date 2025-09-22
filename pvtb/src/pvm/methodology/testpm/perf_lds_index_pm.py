#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LDS Index Performance Model
@author: Li Lizhao
"""
import os,sys,re
from pandas import DataFrame as DF

cdir = os.path.dirname(os.path.realpath(__file__))+'/'
sys.path.append(cdir+'../')

import utility.util as util
from theory.core_performance_theory import ComputeCoreTheory as CCT
from measure.core_performance_measure import ComputeCoreMeasure as CCM
from check.core_performance_check import ComputeCoreCheck as CCC

class LDSIndexPM:
    
    def __init__(self):
        self.theo, self.meas, self.chk = DF(), DF(), DF()
        pass

    @staticmethod
    def acquire_all_tests(test=None, type='theory'):
        """Common function to acquire all tests
        :test: list or None
        """
        ##abs dir is required
        dv = cdir+'../../shader/perf_lds_index.dv'
        test_ptn = "perf_lds_index_(\w+_b\d+)_conflict(\d+)"
        test_param_l = ['iDS', 'cDS']
        test_info_df = util.conv2df(util.get_test_desc(dv, test_ptn, test_param_l))
        if test != None:  
            test_info_df=(test_info_df.set_index(test_info_df['name'])).loc[test,:]
            #reset index to serial number
            test_info_df.reset_index(drop=True, inplace=True)
        if type=='measure':
            return DF(test_info_df['name'])
        else:
            return test_info_df
    
    def theory(self, desc, test=None, **kw):
        """LDS INDEX Theory
        :test: str(command line) or list or None(default, means every test in dv)
        """
        if type(test) == str:
            try: test = eval(test)  #If it's a str([])
            except: test= [test]

        test_info_df = LDSIndexPM.acquire_all_tests(test)
        meta_col = ['name', 'wpg', 'vgpr', 'valu', 'salu', 'lds', 'iDS', 'cDS', 'vop32']
        ##[TODO]Passing missing labels to .loc will be deprecated, fix it at then
        meta_df = DF(test_info_df.loc[:,meta_col], columns=meta_col)
        meta_df['wpg']   = 8
        meta_df['vgpr']  = 1
        meta_df['salu']  = 1
        meta_df['valu']  = 5
        meta_df['vop32'] = meta_df['valu']
        meta_df['lds']   = 1
    
        cct = CCT(desc,meta_df)
        self.theo = cct.get_theory()
        gui = util.PMGui()
        gui.run([self.theo])
        return self.theo
    
    def measure(self, desc, edir='./', test=None, **kw):
        """LDSIndexPM Measure
        :edir: str. It MUST be the parent dir contains sub-dir named as test name. 
        If user'd like to debug on some vecs, please also modify the name of dir to 
        comply with this. Else please use 'quickm' to invoke methods directly
        :test: str(command line) or list or None(default, means every test in dv)
        """
        if type(test) == str:
            try: test = eval(test)  #If it's a str([])
            except: test= [test]
        algo_l = ['spisq_launch',]
        #Just keep the first one to compare with theory to simplify dealing
        if kw.get('check_request'): algo_l = [algo_l[0]]    
        meta_df = LDSIndexPM.acquire_all_tests(test, 'measure')
        meta_df['edir'] = meta_df['name'].apply(lambda x: edir+x+'/')
        meta_df['warmup'] = 1
        meta_df['algo'] = ','.join(algo_l)
        ccm = CCM(desc, meta_df)
        _df = ccm.get_measure()
        _df = _df.drop(['edir', 'warmup'], axis=1)
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
            try: test = eval(test)  #If it's a str([])
            except: test= [test]
        
        meth_desc = util.get_cfg_f(cdir+'../methodology.cfg')
        #chk_df = DF(columns=meth_desc['test_check_col'].split(','))
        self.theory(desc, test)
        self.measure(desc, edir, test, check_request=True)
        chk_df = self.theo.reindex(columns=meth_desc['test_check_col'].split(','))
        #[XXX]The 'name' is updated again here per the same list, if the test output
        #couldn't be found under edir, the value becomes 'TBD'
        chk_df.update(self.meas) 
        ccc = CCC(desc, chk_df)
        chk_df = ccc.get_chk()
        self.chk_df = chk_df
        #gui = util.PMGui()
        #gui.run([chk_df])
        return self.chk_df

if __name__=='__main__':
    opt = util.option_parser()
    ldsi = LDSIndexPM()
    if opt.func == 'theory':
        ldsi.theory(opt.desc, opt.test)
    elif opt.func == 'measure':
        ldsi.measure(opt.desc, opt.edir, opt.test)
    elif opt.func == 'check':
        ldsi.check(opt.desc, opt.edir, opt.test)
    else:
        print('NYI')
        sys.exit()


