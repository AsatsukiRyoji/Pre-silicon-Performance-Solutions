#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sp_v_mmac import *
print("SP_MMAC test name follow format: gkt_perf_sp_[INST]_ipw[I]_wpg[W]\n")
sp_v_mmac_test_ptn = 'gkt_perf_sp_(\S+)_ipw(\d+)_wpg(\d+)'

inst_arg_str, all_args = Sp_mmac_Class.get_args_from_name(sp_v_mmac_test_ptn, INST_ARGS_INST, INST_ARGS_IPW, INST_ARGS_WPG)

if not inst_arg_str and not all_args:
print(f"no args matched from name")

sp_mmac_test = Sp_mmac_Class(inst_arg_str)
sp_mmac_test.gen_output()



