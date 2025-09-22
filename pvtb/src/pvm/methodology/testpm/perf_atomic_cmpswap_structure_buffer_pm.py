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
    'atomic_cmpswap_structure_buffer' : {
        'dv'            : dv_dir + 'perf_atomic_cmpswap_structure_buffer.dv'
        ,'test_ptn'     : "perf_buffer_atomic_cmpswap\w+_structure_buffer_stride(\d+)K_aratio(\d+(\.\d+)?)_mode(\w+)"
        ,'test_param_l' : ['vmemTYPE', 'vmemPAY', 'vmemCAC', 'stride', 'n128', 'bpi', 'csw']  # , 'stride', 'csw'
        ,'warmup'       : 2
    }
}
class AtomicCmpswap_StructureBufferPM(PerfTestPM):

    def __init__(self):
        # call the __init__ func of parent class
        super(AtomicCmpswap_StructureBufferPM, self).__init__()
        # get the key info from perf_test_pm
        self.test_cfg = testpm_cfg_d['atomic_cmpswap_structure_buffer']

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
       
        hit ='TCP'
        #print('hit:',hit)
        if hit=='TCP':
            rdir = kw.get('rdir', None)
            # for ooo test, we only use the algo-spisq_launch_done_ave to get the performance results
            algo = 'spisq_launch_done_ave'
            
            # use below test as the reference test
            #test_off = 'perf_buffer_instruction_ls_ooo_OFF'
            if re.match("perf_buffer_atomic_cmpswap\w+_structure_buffer_stride(\d+)K_aratio(\d+(\.\d+)?)_modeSW_OFF", meta_df['name'][0]):
                test_off = test.replace("SW_OFF", "SW_ON")
            elif re.match("perf_buffer_atomic_cmpswap\w+_structure_buffer_stride(\d+)K_aratio(\d+(\.\d+)?)_modeWT_SW_ON", meta_df['name'][0]):
                test_off = test.replace("WT_SW_ON", "SW_ON")
            else:
                test_off = test
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
        self.chk_df['check'] = self.chk_df.T.apply(lambda x : 'pass' if x['name'].endswith('SW_ON') else x['check'])
        if gui_en:
            gui = util.PMGui()
            gui.run([self.chk_df])
        return self.chk_df
      

if __name__ == '__main__':
    opt = util.option_parser()
    buflv = AtomicCmpswap_StructureBufferPM()
    if opt.func == 'theory':
        buflv.theory(opt.desc, opt.test, opt.gui_en, rdir=opt.rdir)
    elif opt.func == 'measure':
        buflv.measure(opt.desc, opt.algo, opt.edir, opt.test, opt.gui_en)
    elif opt.func == 'check':
        buflv.check(opt.desc, opt.edir, opt.test, opt.gui_en)
    else:
        print('NYI')
        sys.exit()

