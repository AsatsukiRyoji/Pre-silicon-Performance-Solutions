#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sq_data_forwarding import *
sq_data_forwarding_test_ptn = 'sq_data_forwarding_inst1(\S+)_inst2(\S+)_ipw(\d+)_wpg(\d+)'
#default values for inst_args
inst_arg_str, all_args = SqDataForwardingClass.get_args_from_name(sq_data_forwarding_test_ptn, 'TYPE1', 'TYPE2', INST_ARGS_IPW, INST_ARGS_WPG)
sdftest = SqDataForwardingClass(inst_arg_str,all_args)
sdftest.gen_output()



