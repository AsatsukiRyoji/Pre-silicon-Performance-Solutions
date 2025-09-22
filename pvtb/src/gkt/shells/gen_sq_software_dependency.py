#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sq_software_dependency import *
sq_software_dependency_test_ptn = 'sq_software_dependency_inst1(\S+)_inst2(\S+)_ipw(\d+)_wpg(\d+)'
#default values for inst_args
TYPE1 = 'valu_write_vcc'
TYPE2 = 'valu_read_vccz'
inst_arg_str, all_args = SqSoftwareDependencyClass.get_args_from_name(sq_software_dependency_test_ptn, TYPE1, TYPE2, INST_ARGS_IPW, INST_ARGS_WPG)
ssdtest = SqSoftwareDependencyClass(inst_arg_str)
ssdtest.gen_output()



