#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../test')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from gkt_util import *
from spi_culock import *
tgid_x_en = 0
tgid_y_en = 0
tgid_z_en = 0
tg_size_en = 0
user_sgpr = 0
vgpr = 1
unorder = 1

