#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from buffersanity import *
buffer_test_ptn = 'buffer_(load|store)_ipw(\d+)_wpg(\d+)_dwpi(\d+)_comp(\d+)_hit(\w+)'
# inst args will be formatted as "-i mem_type load -i ipw 4..." returned in inst_arg_str
# all args will be collected in dict returned in all_args
inst_arg_str, all_args = BufferClass.get_args_from_name(buffer_test_ptn,
INST_ARGS_MEMTYPE, INST_ARGS_IPW, INST_ARGS_WPG, INST_ARGS_DWPI, INST_ARGS_COMP, INST_ARGS_HIT)
if not inst_arg_str and not all_args:
print(f"no args matched from name")

# do other things on all_args
buftest = BufferClass(inst_arg_str)
buftest.gen_output()

