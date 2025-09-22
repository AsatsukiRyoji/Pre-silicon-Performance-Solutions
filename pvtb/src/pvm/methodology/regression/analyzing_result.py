#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,sys,re,time, pdb, glob, subprocess
from pandas import DataFrame as DF
import pandas as pd
import numpy as np
from pandas import Series as SE
import multiprocessing.dummy as md
import argparse

cdir = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(cdir +'../')
from utility import util
from utility import pmplot

stem = os.environ.get('STEM')+'/' if os.environ.get('STEM') else cdir + '../../../../../../../'

from core_performance_regression import RegrSystem as RS

Descript = '''
    ./
    1. apy analyzing_result.py -m postproc
        eg. cmd: apy analyzing_result.py -m postproc
            Execute this command during the regression run. The completed tests will be summarized into the \'temporary_regression_result.csv\'.
    2. apy analyzing_result.py -l timelable 
        eg. cmd: apy analyzing_result.py -l 231130
            After regression. This command separates \'*231130.csv\' file into groups.
    3. apy analyzing_result.py -s str1 str2
        eg. cmd: apy analyzing_result.py -s mmac vcs_run.log
            Searches for test with \'*mmac*\' in the test name, and print test_dir + \'/vcs_run.log\' to \'search_test_file.log\', you can view it with the shortcut key \'gf\'
        eg. cmd: apy analyzing_result.py -s mmac sp3
            Searches for test with \'*mmac*\' in the test name, and print test_dir + \'/*sp3*\' to \'search_test_file.log\', you can view it with the shortcut key \'gf\'
    4. apy analyzing_result.py -c tar_csv_timelabel [shader|cache|command] [shader\'s csv_timelabel]
        eg. cmd: apy analyzing_result.py -c 231130 shader 231128
            Read the \'*231128.csv\' file in the shader tree path, and write it to the \'*231130.csv\' file. (This command has limitations)
    cd regression_result_history/
    5. apy analyzing_result.py
        eg. cmd: apy ../analyzing_result.py
            View the \'pass\' or \'fail\' status of each group of tests in bar charts
    6. apy analyzing_result.py -t testname
        eg. cmd: apy ../analyzing_result.py -t testname
            View historical theoretical and measured values for this test as a discounted graph
'''

def analy_option_parser(type=None):
    
    parser = argparse.ArgumentParser(description='%s' %Descript, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--label', default= None, dest= 'label', help = 'The csv file has postfix of assigned timestring, yymmdd, will be recognized to generate diagram')
    parser.add_argument('-t', '--testname', default= None, dest= 'testname', help= 'Output historical data of one specific test')
    parser.add_argument('-m', '--mode', default= None, dest= 'mode', help= 'Generate the temporary .csv file before ends [postproc]')
    parser.add_argument('-c', '--csv', default= None, dest= 'csv', nargs = 3, help= 'Generate the comprehensive .csv file, three option: 1.tar_csv_timelabel 2.[shader|cache|command] 3.[shader\'s csv_timelabel]')
    parser.add_argument('-s', '--string', default= None, dest= 'string', nargs = 2, help= 'Search for test with \'str1\' in the test name, and search for file with \'str2\' in the file name. eg. <\'perf\'|\'gemm\'|\'intrace\'>')
    options = parser.parse_args()
    return options

def generate_testgroup_result(testtime):
    file = ''.join(glob.glob('./*_regression_result_' + testtime  + '.csv'))
    df = pd.read_csv(file)
    df = df.drop(['Unnamed: 0'], axis=1)
    testlist, grp = {}, {}
    for group in ['CACHE1', 'CACHE2','CACHE3','COMMAND', 'SHADER', 'RERUN']:
        grp.update(util.get_cfg_f(cdir + 'perf_bowen_b0_ip.testlist', True, sec=group))
    for k,v in grp.items():
        ptn = '(\w+)(-sub\d+)?'
        _grp = re.search(r''+ ptn +'', k).groups()
        _g, _s = _grp[0], _grp[1]
        if _s != None and testlist.get(_g) != None:
            testlist[_g].extend([v])
        else:
            testlist[_g] = [v]

    df_d = {}
    for g,t in testlist.items():
        for i in t:
            try:
                _df = df.loc[df['name'].apply(lambda x: True if re.match(r''+i+'$',x) else False)]
                df_d[g] = _df if g not in df_d.keys() else df_d[g].append(_df, ignore_index=True)
            except:
                pass

    for g,d in df_d.items():
        file_name = os.path.splitext(os.path.basename(cdir + file))[0]
        d.to_csv(file_name + '_' + g + '.csv')
    pass

def generate_csv_when_run(mode):
    meth_desc = util.get_cfg_f(cdir+'../methodology.cfg')
    regr_col_l = meth_desc['regression_col'].split(',')
    result_df = DF(columns=regr_col_l)
    if mode == 'postproc':
        try: edir = os.environ.get('PV_GC_OUT')
        except: edir = meth_desc['default_output_home'] %(stem)
        for d in os.listdir(edir):
            f = d + '_perf_check_result.csv'
            try:
                _ = pd.read_csv(edir+d+'/'+f).drop(['Unnamed: 0'], axis = 1)
                result_df = result_df.append(_, ignore_index = True)
            except:
                continue
    result_df.to_csv(cdir + 'temporary'+ '_regression_result' +'.csv', float_format = '%.3f',mode = 'w')

def generate_history_comparison_result():
    grp_hist = {}
    for f in os.listdir('./'):
        if f.split('.')[-1] == 'csv': 
            tim = f.split('_')[-1].split('.')[0]
            df = pd.read_csv(f)
            df = df.drop(['Unnamed: 0'], axis=1)
            testlist, grp = {}, {}
            for group in ['CACHE1', 'CACHE2', 'CACHE3', 'COMMAND', 'SHADER', 'RERUN']:
                grp.update(util.get_cfg_f(cdir + 'perf_bowen_b0_ip.testlist', True, sec=group))
        for k,v in grp.items():
            ptn = '(\w+)(-sub\d+)?'
            _grp = re.search(r''+ ptn +'', k).groups()
            _g, _s = _grp[0], _grp[1]
            if _s != None and testlist.get(_g) != None:
                testlist[_g].extend([v])
            else:
                testlist[_g] = [v]

        df_d = {}
        for g,t in testlist.items():
            for i in t:
                try:
                    _df = df.loc[df['name'].apply(lambda x: True if re.match(r''+i+'$',x) else False)]
                    df_d[g] = _df if g not in df_d.keys() else df_d[g].append(_df, ignore_index=True)
                except:
                    pass

        for g,d in df_d.items():
            #d.to_csv(fn + '_' + g + '.csv')
            if not d.empty :
                if grp_hist.get(g):
                    grp_hist[g].update({tim:d})
                else:
                    grp_hist[g] = {tim:d}
    pass

    dir = os.getcwd()
    for grp,dat in grp_hist.items():
        pmplot.plot_passrate(dir, grp, dat)
    for f in os.listdir(dir):
        if f.endswith('png'):
            pmplot.plot_show(f)

def generate_specifictest_history_comparison_result(testname):
    _df = DF()
    for f in os.listdir('./'):
        if '.csv' in f:
            tim = f.split('_')[-1].split('.')[0]
            df = pd.read_csv(f)
            df = df.loc[df.loc[:, 'name'] == testname, ['name', 'check', 'ratio', 'theory', 'measure', 'bottleneck', 'unit']] # method one
            #df = df.loc[df['name'].apply(lambda x: True if x == testname else False), ['name', 'check', 'ratio']] # method two
            #df = df[df['name'].apply(lambda x: True if x == testname else False)][['name','check','ratio']] # method three
            #df = df.apply(lambda x: x.name if x.name == testname else None, axis = 1).dropna() #This method cann't work
            df['time'] = tim
            _df = _df.append(DF(df))
    df = _df.sort_values('time')
    dir = os.getcwd()
    pmplot.plot_test_state(dir, testname, df)
    for f in os.listdir(dir):
        if f.endswith('png'):
            pmplot.plot_show(f)

def generate_comprehensive_csv_file(tar_csv_label, csv_dir, csv_time_label):
    tar_csv_file = ''.join(glob.glob('./*_regression_result_' + tar_csv_label  + '.csv'))
    edir = '/project/bowen/b0/archbox1/corepv/bowenb0_regr_1113_' + csv_dir + '/src/test/suites/block/perf/methodology/regression/'
    csv_file = ''.join(glob.glob(edir + '*_regression_result_' + csv_time_label  + '.csv'))
    df = pd.read_csv(csv_file)
    df = df.drop(['Unnamed: 0'], axis=1)
    df.to_csv(cdir + tar_csv_file, mode = 'a')

def search_test_file(str1, str2):
    out_dir = stem + 'out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/run/block/perf'
    os.chdir(out_dir)
    result, result_out = [],[]
    test_name_dir = [f for f in os.listdir(out_dir) if os.path.isdir(os.path.join(out_dir, f))]
    str1_list = [f for f in test_name_dir if str1 in f]
    for single_test_str1 in str1_list:
        if str2 == 'vcs_run.log':
            result.append(subprocess.getoutput('ls -l ' + single_test_str1 + '/' + 'vcs_run.log'))
        else:
            test_name_file = os.listdir(out_dir + '/' + single_test_str1)
            str2_list = [f for f in test_name_file if str2 in f]
            for single_file_str2 in str2_list:
                result.append(subprocess.getoutput('ls -l ' + single_test_str1 + '/' + single_file_str2))
    result = [s for s in result if 'No such' not in s]
    for single in result:
        print(single)
        single = single.split(' perf')
        single = single[0] + ' ' + out_dir + '/perf' + single[1] + '\n'
        result_out.append(single)
    open(cdir + '/search_test_file.log', 'w').write(''.join(result_out))
    open(out_dir + '/search_test_file.log', 'w').write(''.join(result_out))

if __name__ == '__main__':  #necessary for multiple threading
    opt = analy_option_parser()
    if opt.label:
        generate_testgroup_result(opt.label)
    elif opt.testname:
        generate_specifictest_history_comparison_result(opt.testname)
    elif opt.mode:
        generate_csv_when_run(opt.mode)
    elif opt.csv:
        tar_csv_label, csv_dir, csv_time_label = opt.csv
        generate_comprehensive_csv_file(tar_csv_label, csv_dir, csv_time_label)
    elif opt.string:
        string1, string2 = opt.string
        search_test_file(string1, string2)
    else:
        generate_history_comparison_result()
    pass

    ##NOTE: To make plot.show() works in subprocess needs extra work.
    #mp = md.Pool(processes=len(grp_hist))
    #for grp,dat in grp_hist.items():
    #    mp.apply_async(pmplot.plot_passrate, args=(grp, dat))
    #mp.close()
    #mp.join()

