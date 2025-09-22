#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pandas import Series as SE
from pandas import DataFrame as DF
import numpy as np
import matplotlib
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import PIL
from PIL import Image

#def plot_option_parser(type=None):
#    
#    parser = argparse.ArgumentParser(description='%s options' %type, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#    parser.add_argument('-n', '--name', default= 'plot', dest= 'name', help = 'plot name')
#    options = parser.parse_args()
#
#    return options

matplotlib.use('tkagg')
def plot_passrate(dir, name, hist):
    '''Plotting passrate
    :hist: historical data of one plot
    '''
    os.chdir(dir)
    plt.cla()   ##Must clean out data to prevent accumulated on savfig
    x_coord = sorted(hist)
    ind = [i for i,_ in enumerate(x_coord)]
    fai_over, fai, fai_under, pas = [], [], [], []
    for x in x_coord:
        _v = hist[x].loc[:,'check'].value_counts()
        try:
            fai_over.append(_v['overfail'])
        except:
            fai_over.append(0)       
        try:
            fai.append(_v['fail'])
        except:
            fai.append(0)       
        try:
            fai_under.append(_v['underfail'])
        except:
            fai_under.append(0)
        try:
            pas.append(_v['pass'])
        except:
            pas.append(0)
        
    fails_over = SE(fai_over)
    fails = SE(fai)
    fails_under = SE(fai_under)
    passes = SE(pas)

    fig = plt.figure(figsize = (10, 6.18))
    fig.clear()
    p_over = plt.bar(ind, fails_over.apply(lambda x: np.nan if x == 0 else x), width=0.5, label='overfail', color = 'lightcoral', bottom = passes + fails_under + fails)
    p = plt.bar(ind, fails.apply(lambda x: np.nan if x == 0 else x), width=0.5, label='fail', color = 'red', bottom = passes + fails_under)
    p_under = plt.bar(ind, fails_under.apply(lambda x: np.nan if x == 0 else x), width=0.5, label='underfail', color = 'firebrick', bottom = passes)
    p_pass = plt.bar(ind, passes.apply(lambda x: np.nan if x ==0 else x),width = 0.5, label = 'pass', color = 'green')
    plt.bar_label(p_over, label_type = 'center')
    plt.bar_label(p, label_type = 'center')
    plt.bar_label(p_under, label_type = 'center')
    plt.bar_label(p_pass, label_type = 'center')
    plt.xticks(ind, x_coord, rotation = 45)
    plt.ylabel("check")
    plt.xlabel("date")
    plt.legend(loc = "lower left")
    plt.title(name)
    plt.savefig(name+'.png', format='png', bbox_inches='tight')
    plt.close(fig)
    #for x, y in enumerate(fails):
     #   plt.text(x, y+1, '%s' %round(y,1), ha='center')
    #plt.show()

def plot_test_state(dir, testname, hist):
    os.chdir(dir)
    plt.cla()   
    fig = plt.figure(figsize = (10, 6.18))
    fig.clear()
    p_theory = plt.plot([str(i) for i in hist.time], [str(i) for i in hist.theory], 'bs-', alpha = 0.7, linewidth = 3, label = 'theory') # draw the theory
    theo_valu, measure_valu = [], []
    count_theo_text, count_meas_inc, count_meas_dec, count_meas_keep = 0, 0, 0 ,0
    for i  in hist.theory.tolist(): #write value on theory line
        theo_valu.append(i)
        theo_len = len(theo_valu)
        if theo_len != 1 and theo_valu[theo_len-1] != theo_valu[theo_len-2]: # write the theory value on the theory line if have change
            plt.text(hist.time.tolist()[theo_len-1], hist.theory.tolist()[theo_len-1], hist.theory.tolist()[theo_len-2], color = 'blue', ha = 'right', va = 'bottom')
            count_theo_text = count_theo_text + 1
    if count_theo_text == 0 : # if theory only one value, write the value only once
        plt.text(hist.time.tolist()[0], hist.theory.tolist()[0], hist.theory.tolist()[0], color = 'blue', ha = 'right', va = 'bottom')
    for i in hist.measure: # draw the measure
        measure_valu.append(float(i))
        meas_len = len(measure_valu)
        if meas_len != 1 and (measure_valu[meas_len-1] - measure_valu[meas_len-2]) / measure_valu[meas_len-2] >= 0.05: #second than first value, measure increase>=5%
            count_meas_inc = count_meas_inc + 1
            if count_meas_inc == 1: # draw the label only once 
                p_measure = plt.plot(hist.time.tolist()[meas_len-2 : meas_len], measure_valu[meas_len-2 : meas_len], 'c*-', alpha = 0.95, linewidth = 2, label = 'measure increase>=5%') 
            else:
                p_measure = plt.plot(hist.time.tolist()[meas_len-2 : meas_len], measure_valu[meas_len-2 : meas_len], 'c*-', alpha = 0.95, linewidth = 2) 
        elif meas_len != 1 and (measure_valu[meas_len-2] - measure_valu[meas_len-1]) / measure_valu[meas_len-2] >= 0.05: #second than first value, measure decrease>=5%
            count_meas_dec = count_meas_dec + 1
            if count_meas_dec == 1: # draw the label only once 
                p_measure = plt.plot(hist.time.tolist()[meas_len-2 : meas_len], measure_valu[meas_len-2 : meas_len], color = 'peru', linestyle = '-', marker = '*', alpha = 0.95, linewidth = 2, label = 'measure decrease>=5%') 
            else:
                p_measure = plt.plot(hist.time.tolist()[meas_len-2 : meas_len], measure_valu[meas_len-2 : meas_len], color = 'peru', linestyle = '-',  marker = '*', alpha = 0.95, linewidth = 2)
        elif meas_len != 1: #second than first value, measure keep in 5%
            count_meas_keep = count_meas_keep + 1
            if count_meas_keep == 1: # draw the label only once 
                p_measure = plt.plot(hist.time.tolist()[meas_len-2 : meas_len], measure_valu[meas_len-2 : meas_len], 'm*-', alpha = 0.95, linewidth = 2, label = 'measure keep<=5%')             
            else:
                p_measure = plt.plot(hist.time.tolist()[meas_len-2 : meas_len], measure_valu[meas_len-2 : meas_len], 'm*-', alpha = 0.95, linewidth = 2)
    for i, tick in enumerate(plt.gca().get_xticklabels()): # add color to the X-axis scale
        if i < len(hist.measure.tolist()) and hist.check.tolist()[i] == 'pass':
            tick.set_color('green')
            #plt.text(hist.time.tolist()[i], hist.measure.tolist()[i], 'Pass', color = 'green', ha='center', va='top') # write Pass or Fail on the line
        elif i < len(hist.check.tolist()):
            tick.set_color('darkred')
            #plt.text(hist.time.tolist()[i], hist.measure.tolist()[i], 'Fail', color = 'red', ha='left', va='bottom')
    plt.legend()
    plt.xlabel('time')
    plt.ylabel(hist.unit.tolist()[1])# y-axis unit
    plt.title(testname)
    plt.xticks(rotation =45)
    plt.savefig(testname+'.png', format='png', bbox_inches='tight')
    plt.close(fig)



def plot_show(img_f):
    img= Image.open(img_f)
    img.show()


