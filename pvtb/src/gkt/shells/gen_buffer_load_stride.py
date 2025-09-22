#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from buffer_load_stride import *
buffer_load_stride_test_ptn = 'perf_structure(\d)_buffer_load_dwordx(\d)_comp(\d)_hit([a-zA-Z]+)_ipw(\d+)_wpg(\d+)_so(\d)_bankhash_stride(\d+(?:K|B))_N128B(\d+)_csw(\w+)_isize(\d)'
inst_arg_str, all_args = BufferLoadStrideClass.get_args_from_name(buffer_load_stride_test_ptn,
INST_ARGS_STRUCTURE, INST_ARGS_DWPI, INST_ARGS_COMP, INST_ARGS_HIT, INST_ARGS_IPW, INST_ARGS_WPG, INST_ARGS_SOFFSET, INST_ARGS_STRIDE, INST_ARGS_N128B, INST_ARGS_SWIZZLE_ENABLE, INST_ARGS_IS)
buffer_load_stride = BufferLoadStrideClass(inst_arg_str)

buffer_load_stride.tci, buffer_load_stride.tri, buffer_load_stride.icw, buffer_load_stride.irw, buffer_load_stride.wcg, buffer_load_stride.wrg, buffer_load_stride.tgc, buffer_load_stride.tgr = buffer_load_stride.gen_gemm_param(buffer_load_stride.inst_args[INST_ARGS_DWPI], buffer_load_stride.inst_args[INST_ARGS_STRIDE], buffer_load_stride.inst_args[INST_ARGS_TPW], buffer_load_stride.inst_args[INST_ARGS_WPG])
buffer_load_stride.gen_output()



