#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from matrix_load_gemm import *
# 1. define test name pattern
matrix_load_test_ptn = '(matrix_load_(?:\d+x\d+)?_?b\d+)_hit([A-Z]+)_sw(\d+)_r(\d)_t(\d)_alt(\d+)_bps(\d+)_ipw(\d+)_wpg(\d+)_lds'

# 2. call a static method in TestBase class to parse testname
# inst args will be formatted as "-i mem_type load -i ipw 4..." returned in inst_arg_str
# all args will be collected in dict returned in all_args
inst_arg_str, all_args = MatrixLoadClass.get_args_from_name(matrix_load_test_ptn,
INST_ARGS_INST, INST_ARGS_HIT, INST_ARGS_SWIZZLE_ENABLE, INST_ARGS_R, INST_ARGS_T, INST_ARGS_ALT, INST_ARGS_BPS, INST_ARGS_IPW, INST_ARGS_WPG)

# 3. if not matched, inst_arg_str is "" and all_args is empty dict
if not inst_arg_str and not all_args:
print(f"no args matched from name")
# exit -1

# 4. do other things on all_args(optional)

# 5. normal test generation
mlsbtest = MatrixLoadClass(inst_arg_str)
mlsbtest.gen_output()

