#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sp_vector_alu import *
print("Sp_Vector_Alu test name follow format: gkt_perf_sp_[INST]_edc[E]_ipw[I]_wpg[W]\n")
print("edc option will be off, or 0, by test.dv in replay flow in RDN, and on, or 1, is default\n")

test_ptn = 'perf_sp_(\w+)_edc(\d+)_ipw(\d+)_wpg(\d+)'
inst_arg_str, all_args = Sp_Vector_Alu_Class.get_args_from_name(test_ptn, INST_ARGS_INST, "edc", INST_ARGS_IPW, INST_ARGS_WPG)
if not inst_arg_str and not all_args:
print(f"no args matched from name")

sp_vector_alu_test = Sp_Vector_Alu_Class(inst_arg_str)
sp_vector_alu_test.gen_output()



