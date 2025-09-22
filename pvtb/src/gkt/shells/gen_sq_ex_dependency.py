#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sq_ex_dependency import *
print("test name follow format: sq_ex_dependency_senario[S]_depend[D]_inst1[INST1]_inst2[INST2]_wpg[W]_ipw[I]\n")
sq_ex_dependency_test_ptn = 'sq_ex_dependency_senario(\d+)_depend(\S+)_inst1(\S+)_inst2(\S+)_wpg(\d+)_ipw(\d+)'
inst_arg_str, all_args = SqExDependencyClass.get_args_from_name(sq_ex_dependency_test_ptn, "senario", "depend", "inst1", "inst2", INST_ARGS_WPG, INST_ARGS_IPW)
if not inst_arg_str and not all_args:
print(f"no args matched from name")

ssdtest = SqExDependencyClass(inst_arg_str, all_args)
ssdtest.gen_output()



