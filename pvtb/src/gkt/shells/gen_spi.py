#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from spi import *
spi_test_ptn = ['perf_spi_launch_initgpr_sgpr(0|4|8|16|20)_vgpr(0|1|2)_unorder(ON|OFF)_ipw(1)_wpg(4|16)',
'perf_spi_launch_crawler_ipw(192|256)_tg(288|360)_wpg(4|8)_pip(1|2)',
'perf_spi_launch_culock_ipw(32|64)_tg(72|144|576)_wpg(2|4)_pip(1|2|3|4)',
'perf_spi_launch_pipe_ipw(1)_tg(72)_wpg(16)_pip(2|3|4)'
]
for ptn in spi_test_ptn:
if "perf_spi_launch_initgpr" in ptn:
inst_arg_str, all_args = SpiClass.get_args_from_name(ptn,
INST_ARGS_USER_SGPR, INST_ARGS_TIDIG_COMP_CNT, TEST_ARGS_UNORDER, INST_ARGS_IPW, INST_ARGS_WPG)
else:
inst_arg_str, all_args = SpiClass.get_args_from_name(ptn,
INST_ARGS_IPW, INST_ARGS_TG_X, INST_ARGS_WPG, "pip")

if not inst_arg_str and not all_args:
print(f"no args matched from name")
continue
else:
print(inst_arg_str)
print(all_args)

# do other things on all_args
spitest = SpiClass(inst_arg_str, all_args)
spitest.gen_output()




