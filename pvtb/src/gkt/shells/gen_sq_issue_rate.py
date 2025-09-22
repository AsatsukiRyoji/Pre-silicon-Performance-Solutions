#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from sq_issue_rate import *
sq_issue_rate_test_ptn = 'sq_issue_rate_(\S+)_ipw(\d+)_wpg(\d+)'
#default values for inst_args
#TYPE1 = 'salu'
inst_arg_str, all_args = SqIssueRateClass.get_args_from_name(sq_issue_rate_test_ptn, INST_ARGS_INST, INST_ARGS_IPW, INST_ARGS_WPG)
sdftest = SqIssueRateClass(inst_arg_str)
sdftest.gen_output()



