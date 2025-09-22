#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sp_trans import *
print("SP_trans test name follow format: gkt_perf_sp_[INST]_edc[E]_ipw[I]_wpg[W]\n")
print("edc option will be off, or 0, by test.dv in replay flow in RDN, and on, or 1, is default\n")

sp_trans_test_ptn = 'gkt_perf_sp_(\S+)_ipw(\d+)_wpg(\d+)'

inst_arg_str, all_args = Sp_Trans_Class.get_args_from_name(sp_trans_test_ptn, INST_ARGS_INST, INST_ARGS_IPW, INST_ARGS_WPG)

if not inst_arg_str and not all_args:
print(f"no args matched from name")

sp_trans_test = Sp_Trans_Class(inst_arg_str)
sp_trans_test.gen_output()



