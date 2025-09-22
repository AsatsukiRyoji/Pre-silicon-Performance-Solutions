#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bankhash result analysis file
1. confirm stride_lst items
2. confirm case_ptn
3. usage: python3 hash_ana_pm.py dealed_file isize_num
dealed_file: one .csv file
isize_num: 0|1|2|3
"""
import pandas as pd
import re, sys
import matplotlib.pyplot as plt
#f_ana = str(sys.argv[1])

stride_lst = ['128B', '256B', '512B', '1K', '2K', '3K', '4K', '8K', '64K', '8192K']

dwx1_ipw32_bankhash1  = {k:0 for k in stride_lst}
dwx1_ipw64_bankhash1  = {k:0 for k in stride_lst}
dwx1_ipw32_bankhash0  = {k:0 for k in stride_lst}
dwx1_ipw64_bankhash0  = {k:0 for k in stride_lst}
dwx1_ipw32_sub        = {k:0 for k in stride_lst}
dwx1_ipw64_sub        = {k:0 for k in stride_lst}

dwx2_ipw16_bankhash1  = {k:0 for k in stride_lst}
dwx2_ipw32_bankhash1  = {k:0 for k in stride_lst}
dwx2_ipw16_bankhash0  = {k:0 for k in stride_lst}
dwx2_ipw32_bankhash0  = {k:0 for k in stride_lst}
dwx2_ipw16_sub        = {k:0 for k in stride_lst}
dwx2_ipw32_sub        = {k:0 for k in stride_lst}

dwx4_ipw8_bankhash1   = {k:0 for k in stride_lst}
dwx4_ipw16_bankhash1  = {k:0 for k in stride_lst}
dwx4_ipw8_bankhash0   = {k:0 for k in stride_lst}
dwx4_ipw16_bankhash0  = {k:0 for k in stride_lst}
dwx4_ipw8_sub         = {k:0 for k in stride_lst}
dwx4_ipw16_sub        = {k:0 for k in stride_lst}

case_ptn = "buffer_load\w*_dwordx%d\w*_ipw%d\w*_bankhash%d\w*" + "_isize%0d"%(int(sys.argv[2]))
stride_ptn = "\d+(K|B)"
stride = "x" # default value

def solve_sub(dwxx_ipwx_bankhash1, dwxx_ipwx_bankhash0, dwxx_ipwx_sub):
    for i, v in dwxx_ipwx_bankhash1.items():
        dwxx_ipwx_sub[i] = dwxx_ipwx_bankhash1[i] - dwxx_ipwx_bankhash0[i]

def draw(row, column, num, dwxx_ipwx_bankhash1, dwxx_ipwx_bankhash0, dwxx_ipwx_sub, t):

    x = fig.add_subplot(row, column, num)
    s_dwxx_ipwx_bankhash1 = pd.Series(dwxx_ipwx_bankhash1, index = stride_lst)
    p_dwxx_ipwx_bankhash1 = s_dwxx_ipwx_bankhash1.plot(kind = 'line', alpha = 0.5, rot = 0, grid = True, title = t, label = "bankhash1")
    p_dwxx_ipwx_bankhash1.legend(fontsize=6)
    p_dwxx_ipwx_bankhash1.set_xlabel("stride")
    p_dwxx_ipwx_bankhash1.set_ylabel("tcc_tcr_bw")
    for i, v in enumerate(s_dwxx_ipwx_bankhash1):
        p_dwxx_ipwx_bankhash1.text(i, v+0.01, str(v),  ha = 'center', rotation = 0)
    
    x = fig.add_subplot(row, column, num)
    s_dwxx_ipwx_bankhash0 = pd.Series(dwxx_ipwx_bankhash0, index = stride_lst)
    p_dwxx_ipwx_bankhash0 = s_dwxx_ipwx_bankhash0.plot(kind = 'bar', alpha = 0.5, rot = 0, grid = True, color = "red", label = "bankhash0")
    p_dwxx_ipwx_bankhash0.legend(fontsize=6)
    for i, v in enumerate(s_dwxx_ipwx_bankhash0):
        p_dwxx_ipwx_bankhash0.text(i, v-0.05, str(v),  ha = 'center', rotation = 0)

    x = fig.add_subplot(row, column, num)
    s_dwxx_ipwx_sub = pd.Series(dwxx_ipwx_sub, index = stride_lst)
    dwxx_ipwx_bankhash0_value = [dwxx_ipwx_bankhash0[key] for key in stride_lst]
    p_dwxx_ipwx_sub  = s_dwxx_ipwx_sub.plot(kind = 'bar', bottom = dwxx_ipwx_bankhash0_value, alpha = 0.5, rot = 0, grid = True, color = "green", label = "bankhash1-bankhsh0")
    p_dwxx_ipwx_sub.legend(fontsize=6)

with open(str(sys.argv[1]), 'r') as f:
    ls = f.readlines()

for l in range(len(ls)):
    result = ls[l].split(',')
    if re.search(case_ptn%(1, 32, 1), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx1_ipw32_bankhash1[stride.group()] = float(result[2])
    elif re.search(case_ptn%(1, 32, 0), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx1_ipw32_bankhash0[stride.group()] = float(result[2])
    elif re.search(case_ptn%(1, 64, 1), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx1_ipw64_bankhash1[stride.group()] = float(result[2])
    elif re.search(case_ptn%(1, 64, 0), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx1_ipw64_bankhash0[stride.group()] = float(result[2])
    elif re.search(case_ptn%(2, 16, 1), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx2_ipw16_bankhash1[stride.group()] = float(result[2])
    elif re.search(case_ptn%(2, 16, 0), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx2_ipw16_bankhash0[stride.group()] = float(result[2])
    elif re.search(case_ptn%(2, 32, 1), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx2_ipw32_bankhash1[stride.group()] = float(result[2])
    elif re.search(case_ptn%(2, 32, 0), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx2_ipw32_bankhash0[stride.group()] = float(result[2])
    elif re.search(case_ptn%(4, 8, 1), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx4_ipw8_bankhash1[stride.group()] = float(result[2])
    elif re.search(case_ptn%(4, 8, 0), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx4_ipw8_bankhash0[stride.group()] = float(result[2])
    elif re.search(case_ptn%(4, 16, 1), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx4_ipw16_bankhash1[stride.group()] = float(result[2])
    elif re.search(case_ptn%(4, 16, 0), ls[l]):
        stride = re.search(stride_ptn, ls[l]) # confirm
        dwx4_ipw16_bankhash0[stride.group()] = float(result[2])


solve_sub(dwx1_ipw32_bankhash1, dwx1_ipw32_bankhash0, dwx1_ipw32_sub)
solve_sub(dwx1_ipw64_bankhash1, dwx1_ipw64_bankhash0, dwx1_ipw64_sub)
solve_sub(dwx2_ipw16_bankhash1, dwx2_ipw16_bankhash0, dwx2_ipw16_sub)
solve_sub(dwx2_ipw32_bankhash1, dwx2_ipw32_bankhash0, dwx2_ipw32_sub)
solve_sub(dwx4_ipw8_bankhash1, dwx4_ipw8_bankhash0, dwx4_ipw8_sub)
solve_sub(dwx4_ipw16_bankhash1, dwx4_ipw16_bankhash0, dwx4_ipw16_sub)


fig = plt.figure(figsize = (20, 8))
#fig.text(0.5, 1, "isize", horizontalalignment = 'center', verticalalignment = 'top', fontsize = 20)

draw(2, 3, 1, dwx1_ipw32_bankhash1, dwx1_ipw32_bankhash0, dwx1_ipw32_sub, "dwx1_ipw32")
draw(2, 3, 2, dwx2_ipw16_bankhash1, dwx2_ipw16_bankhash0, dwx2_ipw16_sub, "dwx2_ipw16")
draw(2, 3, 3, dwx4_ipw8_bankhash1, dwx4_ipw8_bankhash0, dwx4_ipw8_sub, "dwx4_ipw8")
draw(2, 3, 4, dwx1_ipw64_bankhash1, dwx1_ipw64_bankhash0, dwx1_ipw64_sub, "dwx1_ipw64")
draw(2, 3, 5, dwx2_ipw32_bankhash1, dwx2_ipw32_bankhash0, dwx2_ipw32_sub, "dwx2_ipw32")
draw(2, 3, 6, dwx4_ipw16_bankhash1, dwx4_ipw16_bankhash0, dwx4_ipw16_sub, "dwx4_ipw16")

pic_name = str(sys.argv[1][:-4])+"_"+"isize"+str(sys.argv[2])+ ".png"
plt.tight_layout()
plt.savefig(pic_name, dpi = 400)
plt.clf()


