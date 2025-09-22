#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from buffer_copy import *
# 1. define test name pattern
buffer_copy_test_ptn = 'buffer_copy_ipw(\d+)_wpg(\d+)_dwpi(\d+)_comp(\d+)_hit([A-Z]+)'

# 2. call a static method in TestBase class to parse testname
# inst args will be formatted as "-i mem_type load -i ipw 4..." returned in inst_arg_str
# all args will be collected in dict returned in all_args
inst_arg_str, all_args = BufferCopyClass.get_args_from_name(buffer_copy_test_ptn,
INST_ARGS_IPW, INST_ARGS_WPG, INST_ARGS_DWPI, INST_ARGS_COMP, INST_ARGS_HIT)

# 3. if not matched, inst_arg_str is "" and all_args is empty dict
if not inst_arg_str and not all_args:
print(f"no args matched from name")
# exit -1

# 4. do other things on all_args(optional)

# 5. normal test generation
bufcopytest = BufferCopyClass(inst_arg_str)

bufcopytest.gen_output()
