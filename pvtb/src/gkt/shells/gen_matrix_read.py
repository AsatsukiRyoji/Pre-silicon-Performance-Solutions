#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from matrix_read import *
matrix_read_test_ptn = 'matrix_read_(\d+)wave_(\d+)xdw(\d+)_stride(\d+)_tg(\d+)_hit(\w+)_wm(\d+)'
# inst args will be formatted as "-i mem_type load -i ipw 4..." returned in inst_arg_str
# all args will be collected in dict returned in all_args
inst_arg_str, all_args = MatrixReadClass.get_args_from_name(matrix_read_test_ptn,
INST_ARGS_WPG, INST_ARGS_IPW, INST_ARGS_DWPI, INST_ARGS_STRIDE, INST_ARGS_TG_X, INST_ARGS_HIT, INST_ARGS_WM_UTCL1)
if not inst_arg_str and not all_args:
print(f"no args matched from name")
print(inst_arg_str)
matrix_read_test = MatrixReadClass(inst_arg_str)
matrix_read_test.tci, \
matrix_read_test.tri, \
matrix_read_test.icw, \
matrix_read_test.irw, \
matrix_read_test.wcg, \
matrix_read_test.wrg, \
matrix_read_test.tgc, \
matrix_read_test.tgr = matrix_read_test.gen_gemm_param(matrix_read_test.inst_args[INST_ARGS_TG_X], \
matrix_read_test.inst_args[INST_ARGS_DWPI], \
matrix_read_test.inst_args[INST_ARGS_STRIDE], \
matrix_read_test.inst_args[INST_ARGS_TPW], \
matrix_read_test.inst_args[INST_ARGS_WPG])
matrix_read_test.gen_output()



