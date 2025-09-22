#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sqc import *
sqc_test_ptn = 'sqc_(s_load_dword)_glc(\d+)_ipw(\d+)_wpg(\d+)'
# inst args will be formatted as " -i ipw [IPW] -i wpg [WPG] -i glc 0 -i inst [INST]..." returned in inst_arg_str
# all args will be collected in dict returned in all_args
inst_arg_str, all_args = SqcClass.get_args_from_name(sqc_test_ptn,
INST_ARGS_INST, INST_ARGS_GLC, INST_ARGS_IPW, INST_ARGS_WPG)
print(inst_arg_str)
print(all_args)
if not inst_arg_str and not all_args:
print(f"no args matched from name")

# do other things on all_args
svrtest = SqcClass(inst_arg_str)
svrtest.gen_output()


