#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from buffer_load_cu_align import *
buffer_load_cu_align_test = Buffer_Load_cu_aign_Class()
buffer_load_cu_align_test.tci, buffer_load_cu_align_test.tri, buffer_load_cu_align_test.icw, buffer_load_cu_align_test.irw, buffer_load_cu_align_test.wcg, buffer_load_cu_align_test.wrg, buffer_load_cu_align_test.tgc, buffer_load_cu_align_test.tgr = buffer_load_cu_align_test.gen_gemm_param(buffer_load_cu_align_test.inst_args[INST_ARGS_DWPI], buffer_load_cu_align_test.inst_args[INST_ARGS_STRIDE], buffer_load_cu_align_test.inst_args[INST_ARGS_TPW], buffer_load_cu_align_test.inst_args[INST_ARGS_WPG], buffer_load_cu_align_test.inst_args[INST_ARGS_IPW])
buffer_load_cu_align_test.gen_output()

