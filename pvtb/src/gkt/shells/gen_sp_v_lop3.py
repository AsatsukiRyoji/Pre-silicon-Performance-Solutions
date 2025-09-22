#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sp_v_lop3 import *
print("V_Lop3_B32 test name follow format: gkt_perf_lop3_ipw[I]_wpg[W]\n")
print("edc option will be off, or 0, by test.dv in replay flow in RDN, and on, or 1, is default\n")

v_lop3_b32_test_ptn = 'gkt_perf_lop3_ipw(\d+)_wpg(\d+)'

inst_arg_str, all_args = V_Lop3_B32_Test.get_args_from_name(v_lop3_b32_test_ptn, INST_ARGS_IPW, INST_ARGS_WPG)

if not inst_arg_str and not all_args:
print(f"no args matched from name")

print(inst_arg_str)

v_lop3_b32_test = V_Lop3_B32_Test(inst_arg_str)
v_lop3_b32_test.gen_output()
