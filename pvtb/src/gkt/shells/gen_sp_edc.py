#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sp_edc import *
test_ptn = 'perf_sp_valu_(\w+)_ipw(\d+)_wpg(\d+)_edc(\w+)'
inst_arg_str, all_args = SpValuEdcClass.get_args_from_name(test_ptn, INST_ARGS_INST, INST_ARGS_IPW, INST_ARGS_WPG, "edc")
if not inst_arg_str and not all_args:
print(f"no args matched from name")

sp_edc_test = SpValuEdcClass(inst_arg_str)
sp_edc_test.gen_output()


