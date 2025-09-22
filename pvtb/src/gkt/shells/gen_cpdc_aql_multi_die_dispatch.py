#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from cpdc_aql_multi_die_dispatch import *
cpdc_test_ptn = "perf_cp_dc_aql_multi_die_dispatch_dpq1_dimx(\d+)_dimy(\d+)_dimz(\d+)_tpgx(\d+)_wpg(\d+)"
inst_arg_str, all_args = CpDc_multi_die.get_args_from_name(cpdc_test_ptn,
INST_ARGS_GRID_SIZE_X, INST_ARGS_GRID_SIZE_Y,INST_ARGS_GRID_SIZE_Z,INST_ARGS_WORKGROUP_SIZE_X, INST_ARGS_WPG)
if not inst_arg_str and not all_args:
print(f"no args matched from name")
cpdc_test_1 = CpDc_multi_die(inst_arg_str)
#cpdc_test_2 = CpDc(inst_arg_str)

