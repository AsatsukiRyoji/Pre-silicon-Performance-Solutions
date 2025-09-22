#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from spi_initgpr import *
inst_ipw = 1
grid_size_x = 72
for workgroup_size_x in {4, 16}:
for usgpr in {0, 4, 8 ,16, 20}:
if usgpr==20:
tgid_x_en = 1
tgid_y_en = 1
tgid_z_en = 1
tg_size_en = 1
user_sgpr = 16
else:
tgid_x_en = 0
tgid_y_en = 0
tgid_z_en = 0
tg_size_en = 0
user_sgpr = usgpr

for vgpr in {0, 1, 2}:
for unorder in {0, 1}:
spitest = SpiClass(grid_size_x*64*workgroup_size_x,workgroup_size_x*64,user_sgpr,tgid_x_en,tgid_y_en,tgid_z_en,tg_size_en,vgpr,unorder,inst_ipw)
spitest.test_args.update({TEST_ARGS_NAME : f"perf_spi_launch_initgpr/perf_spi_launch_initgpr_sgpr{usgpr}_vgpr{vgpr}_unorder{unorder}_ipw{inst_ipw}_wpg{workgroup_size_x}"})
print(spitest.test_args[TEST_ARGS_NAME])
spitest.gen_output()




