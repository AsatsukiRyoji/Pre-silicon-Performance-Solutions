#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Performance Check Model
@author: Li Lizhao
"""

import os, sys, pdb, re
cdir = os.path.dirname(os.path.realpath(__file__))+'/'
sys.path.append(cdir+'../')
import utility.util as util
#import pdb

testpm_map = {
    'perf_buffer_store'             :   'BufferStorePM',
    'perf_buffer_load'              :   'BufferLoadPM',
    'perf_buffer_atomic'            :   'BufferAtomicPM',
    'perf_buffer_ooo'               :   'BufferOooPM',
    'perf_buffer_load_to_lds'       :   'BufferLoadtoLdsPM',
    'perf_buffer_load_to_lds_wrap'  :   'BufferLoadtoLdsWrapPM',
    'perf_buffer_load_hash'         :   'BufferLoadHashPM',
    'perf_buffer_load_align'        :   'BufferLoadAlignPM',
    'perf_global_store'             :   'GlobalStorePM',
    'perf_global_load'              :   'GlobalLoadPM',
    'perf_global_atomic'            :   'GlobalAtomicPM',
    'perf_global_ooo'               :   'GlobalOooPM',
    'perf_global_load_to_lds'       :   'GlobalLoadtoLdsPM',
    'perf_global_load_to_lds_wrap'  :   'GlobalLoadtoLdsWrapPM',
    'perf_global_load_align'        :   'GlobalLoadAlignPM',
    'perf_flat_load'                :   'FlatLoadPM',
    'perf_flat_load_to_lds'         :   'FlatLoadtoLdsPM',
    'perf_flat_load_from_lds_and_mem' : 'FlatLoadFromLdsandMemPM',
    'perf_flat_store'               :   'FlatStorePM',
    'perf_matrix_copy'              :   'MatrixCopyPM',
    'perf_matrix_copy_to_lds'       :   'MatrixCopytoLdsPM',
    'perf_matrix_load_to_lds'       :   'MatrixLoadtoLdsPM',
    'perf_spi_launch'               :   'SPIWaveLaunchPM',
    'perf_spi_launch_initgpr'       :   'SPIWaveLaunchInitGprPM',
    'perf_spi_launch_crawler'       :   'SPIWaveLaunchCrawlerPM',
    'perf_spi_launch_pipe'          :   'SPIWaveLaunchPipePM',
    'perf_spi_launch_culock'        :   'SPIWaveLaunchCulockPM',
    'perf_sp_v_gemm'                :   'SPValuGemmPM',
    'perf_sp_valu_edc'              :   'SPValuEdcPM',
    'perf_sp_valu'                  :   'SPValuRegularPM',
    'perf_sp_v_trans'               :   'SPTransPM',
    'perf_sp_v_cvt'                 :   'SPPrecisonConversionPM',
    'perf_sp_valu_dpfp'             :   'SPValuDPFPPM',
    'perf_ds'                       :   'DsPM',
    'perf_gds'                      :   'GdsPM',
    'perf_gds_latency'              :   'GdsLtcPM',
    'perf_latency_ds'               :   'LtcDsPM',
    'perf_sq_ex'                    :   'SQExDependencyPM',
    'perf_cp_dispatch'              :   'CPSPIWaveLaunchPM',
    'perf_cp_dc'                    :   'CPDCDispatchPM',
    'perf_cp_dc_dimx_dimy'          :   'CPDCXYDispatchPM',
    'perf_buffer_load_burst'        :   'BufferLoadBurstPM',
    'perf_buffer_store_burst'       :   'BufferStoreBurstPM',
    'perf_structure_buffer'         :   'StructureBufferPM',
    'perf_buffer_load_stride'       :   'BufferLoadStridePM',
    'perf_global_load_stride'       :   'GlobalStridePM',
    'perf_flat_load_stride'         :   'FlatStridePM',
    'perf_atomic_cmpswap_structure_buffer' : 'AtomicCmpswap_StructureBufferPM'

}

from utility.util import *
from testpm.perf_buffer_store_pm import BufferStorePM 
from testpm.perf_buffer_load_pm import BufferLoadPM 
from testpm.perf_buffer_atomic_pm import BufferAtomicPM 
from testpm.perf_buffer_ooo_pm import BufferOooPM 
from testpm.perf_buffer_load_hash_pm import BufferLoadHashPM
from testpm.perf_buffer_load_to_lds_pm import BufferLoadtoLdsPM 
from testpm.perf_buffer_load_to_lds_wrap_pm import BufferLoadtoLdsWrapPM 
from testpm.perf_buffer_load_align_pm import BufferLoadAlignPM
from testpm.perf_global_store_pm import GlobalStorePM 
from testpm.perf_global_load_pm import GlobalLoadPM 
from testpm.perf_global_atomic_pm import GlobalAtomicPM 
from testpm.perf_global_ooo_pm import GlobalOooPM 
from testpm.perf_global_load_to_lds_pm import GlobalLoadtoLdsPM 
from testpm.perf_global_load_to_lds_wrap_pm import GlobalLoadtoLdsWrapPM 
from testpm.perf_global_load_align_pm import GlobalLoadAlignPM
from testpm.perf_flat_load_pm import FlatLoadPM
from testpm.perf_flat_load_to_lds_pm import FlatLoadtoLdsPM
from testpm.perf_flat_store_pm import FlatStorePM
from testpm.perf_flat_load_from_lds_and_mem_pm import FlatLoadFromLdsandMemPM
from testpm.perf_matrix_copy_to_lds_pm import MatrixCopytoLdsPM 
from testpm.perf_matrix_copy_pm import MatrixCopyPM 
from testpm.perf_matrix_load_to_lds_pm import MatrixLoadtoLdsPM 
from testpm.perf_spi_launch_pm import SPIWaveLaunchPM
from testpm.perf_spi_launch_initgpr_pm import SPIWaveLaunchInitGprPM
from testpm.perf_spi_launch_crawler_pm import SPIWaveLaunchCrawlerPM
from testpm.perf_spi_launch_pipe_pm import SPIWaveLaunchPipePM
from testpm.perf_spi_launch_culock_pm import SPIWaveLaunchCulockPM
from testpm.perf_sp_valu_gemm_pm import SPValuGemmPM
from testpm.perf_sp_valu_edc_pm import SPValuEdcPM
from testpm.perf_sp_valu_regular_pm import SPValuRegularPM
from testpm.perf_sp_trans_alu_pm import SPTransPM
from testpm.perf_sp_precision_conversion_alu_pm import SPPrecisonConversionPM
from testpm.perf_sp_valu_dpfp_pm import SPValuDPFPPM
from testpm.perf_ds_pm import DsPM
from testpm.perf_gds_pm import GdsPM
from testpm.perf_gds_latency_pm import GdsLtcPM
from testpm.perf_latency_ds_pm import LtcDsPM
from testpm.perf_sq_ex_dependency_pm import SQExDependencyPM
from testpm.perf_cp_dispatch_pm import CPSPIWaveLaunchPM
from testpm.perf_cp_dc_dispatch_pm import CPDCDispatchPM
from testpm.perf_cp_dc_xy_dispatch_pm import CPDCXYDispatchPM
from testpm.perf_buffer_load_burst_pm import BufferLoadBurstPM
from testpm.perf_buffer_store_burst_pm import BufferStoreBurstPM
from testpm.perf_structure_buffer_pm import StructureBufferPM

from testpm.perf_buffer_load_stride_pm import BufferLoadStridePM
from testpm.perf_global_load_stride_pm import GlobalStridePM
from testpm.perf_flat_load_stride_pm import FlatStridePM
from testpm.perf_atomic_cmpswap_structure_buffer_pm import AtomicCmpswap_StructureBufferPM


def tpc_option_parser(type=None):
    
    parser = argparse.ArgumentParser(description='%s options' %type, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--desc', default= 'bowen_b0_ip', dest= 'desc', help = '<project(kongming/...)>_<environment(core/soc/...)> to pinpoint correct project description file')
    parser.add_argument('-e', '--edir', default= './', dest= 'edir', help = "Test otuput")
    parser.add_argument('-t', '--test', default= None, dest= 'test', help = 'Test name')
    parser.add_argument('--gui', default = False, action='store_true', dest= 'gui_en', help= 'GUI enable')
    options = parser.parse_args()

    return options

class TestPerformanceCheck:

    def __init__(self):
        pass   

    @staticmethod
    def check_sim_status(edir, test):
        if (os.path.isfile(edir + test + '/vcs_run.log.gz')):
            return 'func passed'
        else:
            return 'func failed'

    @staticmethod
    def get_test_check(desc, edir, test, gui_en=False):
        '''Get test check.
        This function is for single test
        :edir: output of target test
        :test: must be a single test
        '''
        #print("cwd is : %s" %(os.getcwd()))
        #print("desc is : %s" %desc)
        #print("edir is : %s" %edir)
        #print("test is : %s" %test)
        edir = edir + '/' if not edir.endswith('/') else edir
        edir = os.getcwd() + '/' if edir == './' else edir
        if edir.endswith(test+'/'):
            edir = edir + '../'
        edir = edir + '/' if not edir.endswith('/') else edir
        tpm_dir = cdir + '/../testpm/'
        
        # TODO it will limit the string of test name
        testpm_map_key = re.search(r'perf_[a-z]+_[a-z]+', test).group(0)
        #pdb.set_trace()
        if 'from' in test:
            testpm_map_key = testpm_map_key + "_from_lds_and_mem"
        elif re.search(r'perf_sp_v_cvt_.*_edc\d+_ipw\d+_wpg\d+', test):
            testpm_map_key = testpm_map_key + "_cvt"
        elif re.search(r'perf_sp_v_(rcp|sqrt|rsq|exp|log|sin|cos).*_edc\d+_ipw\d+_wpg\d+', test):
            testpm_map_key = testpm_map_key + "_trans"
        elif 'LDS' in test or 'lds' in test and 'structure_buffer' not in test:
            testpm_map_key = testpm_map_key + "_to_lds"
        elif 'hash_isize' in test:
            testpm_map_key = testpm_map_key + "_hash"
        elif 'ooo' in test:
            testpm_map_key = re.sub("loadstore(valu)?", "ooo", testpm_map_key) 
        elif 'dpfp' in test:
            testpm_map_key = testpm_map_key + "_dpfp"
        elif 'mmac' in test :
            testpm_map_key = testpm_map_key + "_gemm"
        elif 'gds_latency' in test:
            testpm_map_key = "perf_gds_latency"
        ##elif 'ds_read' in test:
        ##    testpm_map_key = testpm_map_key + "_read"
        elif 'latency_ds' in test:
            testpm_map_key = "perf_latency_ds"
        elif '_ds' in test:
            testpm_map_key = "perf_ds"
        elif 'edc' in test:
            testpm_map_key = testpm_map_key + "_edc"
        elif 'initgpr' in test :
            testpm_map_key = testpm_map_key + "_initgpr"
        elif 'crawler' in test :
            testpm_map_key = testpm_map_key + "_crawler"
        elif 'pipe' in test :
            testpm_map_key = testpm_map_key + "_pipe"
        elif 'culock' in test :
            testpm_map_key = testpm_map_key + "_culock"
        elif 'align' in test:
            testpm_map_key = testpm_map_key + "_align"
        elif 'dimx_dimy' in test:
            testpm_map_key = testpm_map_key + "_dimx_dimy"
        elif 'burst' in test:
            testpm_map_key = testpm_map_key + "_burst"
        elif 'atomic_cmpswap' in test:
            testpm_map_key = "perf_atomic_cmpswap_structure_buffer"
        elif 'stride' in test:
            testpm_map_key = testpm_map_key + "_stride"
        elif 'gds' in test:
            testpm_map_key = "perf_gds"
        else:
            pass

        if 'LDS' in test and 'wrap' in test:
            testpm_map_key = testpm_map_key + "_wrap"
        
        testpm = testpm_map[testpm_map_key]
        pm = eval(testpm)()
        func_result = TestPerformanceCheck.check_sim_status(edir, test)
        pm.check(desc, edir, test, gui_en, func_result = func_result)
        edir = edir.rstrip('../') if edir.endswith('../') else edir
        f = edir+'/'+test+'_perf_check_result.csv'
        if os.path.isfile(f):
            os.system('cp -f '+ f + ' ' + f + '.bak')
            os.remove(f)
        #pdb.set_trace()
        pm.chk_df.to_csv(f, mode='w')
        if gui_en:
            gui = util.PMGui()
            gui.run([pm.chk_df])
        #pdb.set_trace()
        pass
        #else:
        #    print("[PERF CHECK FAILED]No test pm of %s can be found" %test)
        #    sys.exit()

if __name__ == '__main__':
    opt = tpc_option_parser()
    #tpc = TestPerformanceCheck()
    TestPerformanceCheck.get_test_check(opt.desc, opt.edir, opt.test, opt.gui_en)
            


            ##XXX: The dispatched subprocess cannot be traced by pdb. Tried add '-m pdb' on this 
            ##cmd and pdb.set_trace() in testpm file, both will stuck
            #cmd = 'python3 '+tpm_dir+testpm_f+' -f check'+' -d '+desc+' -e '+edir+' -t '+test
            #chk_df = call_from_sys(cmd)

