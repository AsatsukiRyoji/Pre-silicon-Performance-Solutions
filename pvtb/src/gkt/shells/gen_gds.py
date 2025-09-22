#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from gds import *
gds_test_ptn = 'perf_gds_(\w+)_ipw(\d+)_wpg(\d+)'
inst_arg_str, all_args = GdsClass.get_args_from_name(gds_test_ptn, INST_ARGS_INST, INST_ARGS_IPW, INST_ARGS_WPG)
if not inst_arg_str and not all_args:
print(f"no args matched from name")
svrtest = GdsClass(inst_arg_str)
svrtest.gen_output()


