#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance methodology common utility
@author: Li Lizhao
"""
import os,sys,re,time, pdb
import subprocess, argparse, logging
from collections import OrderedDict
from pandas import DataFrame as DF
if (sys.version_info < (3, 0)):
    print("[ERROR] This script can only work with 'python3'")
    import ConfigParser as configparser
else:
    import configparser
#Where this file is
cdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cdir)

def alist2df(df):
    '''a(ppend) list to dataframe
    :d: list. Should has the same length as df.columns
    '''
    return lambda d: df.append(dict(zip(df.columns,d)), ignore_index=True)

def protector(max_tries=10):
    import getpass, hashlib
    
    key = '6ff7673e16c72f35a2edff9f7e865aeb'
    tries = 0
    while(tries<max_tries):
        s = getpass.getpass('Passwd: ')
        encrypter = hashlib.md5()
        encrypter.update(s.encode('utf-8'))
        if encrypter.hexdigest() == key:
            print('Correct passwd')
            tries = 'PASS'
            break
        else:
            tries += 1
            print('Incorrect passwd, %s tries left' %(max_tries-tries))
            if tries == max_tries:
                tries = 'FAIL'
            continue

    return tries

def col_init(cols, **kw):
    """Initialize the columns of a dict
    :cols: list contains need to be initialized
    :kw: 'default': specific default value, otherwise it's 'na'. Any other specific assignment match keyword from 'cols'
    Return: ordered dict
    """
    d = kw.get('default','na')
    #try:
    #    #If kw has 'default', pop out it and assign d to it's value 
    #    d = kw.pop('default') #if kw['default']!=None else 'na'
    #except:
    #    d = 'na'
    ################
    #**OrderDict: below functions must be invoked ONE BY ONE, include 'return'
    ################
    _= OrderedDict(zip(cols, len(cols)*[d]))
    _.update(kw)
    return _

def call_from_sys(cmd, has_status=False):
    """Call a command from system.
    Deal different situation per python version
    Return: read handler.
    """
    if (sys.version_info > (3, 0)):
        if has_status == False:
            #py2 subprocess has no this getoutput. 3x can also use 2x way
            output = subprocess.getoutput(cmd)
            return output.split()
        else:
            status, output = subprocess.getstatusoutput(cmd)
            return output.split(), status
            #NOTE|return {'result': output.split(), 'status': status}
    else:
        #A handler as a file reader, can be used only once
        r = subprocess.Popen(cmd, shell= True, stdout= subprocess.PIPE, stderr= open(os.devnull,'w')).stdout
        #NOTE|i is byte string type as b'', need to be decoded to str
        return [i.decode() for i in r.readlines() if i != b'\n']

def get_fd_fn(full_file_name):
    _ = re.match(r'([.\w\/]*\/)',full_file_name)
    fd = _.group(0)
    fn = full_file_name.split('/')[-1]
    return fd,fn

def get_cfg_f(cfg_f, has_sec=False, **kw):
    """Get config file
    :cfg_f: abs file name. File must be the format of ConfigParser. File can have any postfix, but only .cfg is default hightlighted in most editor like vim
    :kw: 1)sec: get content of specific section
    Return:: has_sec==True:{sec:{contents/sec}} else:{contents/cfg}. If sec is set, return contents of it, not affected by has_sec
    """
    cfg_h = configparser.ConfigParser()
    cfg_h.read(cfg_f)
    #pdb.set_trace()
    try:
        sec = kw['sec'].upper()
        #If kw['sec'] is introduced, just current content of specific section will be returned
        return dict(cfg_h.items(sec))
    except:
        pass
    cfg_d = {}
    #If the 'BASE' is not be read as the first section, dealing it will flush out child material. So find it at first to deal and popout it also
    for k in cfg_h.keys():
        if k=='BASE':
            base_f = list(cfg_h[k].values())[0]
            _d,_ = get_fd_fn(cfg_f)
            cfg_d = get_cfg_f(_d+base_f, has_sec, **kw)
             #Pop out it to prevent mis-fetch
            cfg_h.pop(k)
            break
    for k in cfg_h.keys():
        if k=='DEFAULT': continue #'DEFAULT' cannot be pop()
        sec_d=dict(cfg_h.items(k))
        if has_sec:
            try:    #If it does exist, update it
                cfg_d[k].update(sec_d)
            except: #else create it
                cfg_d[k] = {}
                cfg_d[k] = sec_d
        else:
            cfg_d.update(sec_d)
    if kw.get('sec_name') and has_sec==True:
        cfg_d = cfg_d[kw['sec_name']]
    return cfg_d

def get_desc(desc,type):
    glb_desc_d = get_cfg_f(cdir+'/../methodology.cfg')
    prj_desc_d = get_cfg_f(cdir+'/../'+glb_desc_d['desc_home']+desc+'.cfg', has_sec=True)
    desc_d = dict()
    if type == 'theory':
        for s in glb_desc_d['theo_sec'].split(','):
            desc_d.update(prj_desc_d[s])
    elif type == 'measure':
        for s in glb_desc_d['meas_sec'].split(','):
            desc_d.update(prj_desc_d[s])
    for k,v in desc_d.items():
        try:
            desc_d[k] = float(v)
        except:
            pass
    return desc_d

def file_finder(edir, fn_ptn):
    """find specific file in the exe_dir
    If files mpatch fname_ptn is gzip file, it will be unzipped
    """
    flist = []
    
    # check if the edir is effective
    if not os.path.isdir(edir):
        print( "%s does not exists" %(edir))
        sys.exit()

    edir = edir + '/' if not edir.endswith('/') else edir
    
    for f in os.listdir(edir):
        if re.search(r'^' + fn_ptn + '', f):
            if f.endswith('gz'):
                print( "gunzip file %s" %(edir + f))
                os.system('gunzip -f '+ edir + f)
                f = re.sub('.gz$', '', f)
            flist.append(f)
    
    if len(flist) == 0:
        print( "No expected file %s under %s" %(fn_ptn, edir))
        sys.exit()
    
    return flist

def roundNdict(_dict,N):
    for k,v in _dict.items():
        if type(v)== float:
            _dict[k]= round(v, N)
    return _dict

def option_parser(type=None):
    
    parser = argparse.ArgumentParser(description='%s options' %type, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--desc', default= 'bowen_b0_ip', dest= 'desc', help = '<project(kongming/...)>_<environment(core/soc/...)> to pinpoint correct project description file')
    parser.add_argument('--gui', default = False, action='store_true', dest= 'gui_en', help= 'GUI enable')
    parser.add_argument('-a', '--algo', default= 'spisq_launch', dest= 'algo', help = 'measure method used to calculate the rate,  the format must be \'["str",...]\'')
    if type == 'regression':
        parser.add_argument('-r', '--regr', default= None, dest= 'regr', help = 'Regression type on different projects. [regular|sanity|rerun]')
        parser.add_argument('-m', '--mode', default= 'postproc', dest= 'mode', help = 'Regression mode of how tests are dispatched. [single|multi|postproc]')
        parser.add_argument('--no_build', default = False, action='store_true', dest= 'no_build', help= 'No building is required for regression')
        #action means that if acting key '--exe' detected, exe will be true.
        parser.add_argument('--exe', default = False, action='store_true', dest= 'exe', help= 'Execute the regression, by default it only print commands')
        parser.add_argument('--dump', default = False, action='store_true', dest= 'dump', help= 'Add this option to dump the waves')
        parser.add_argument('--hash_en', default = False, action='store_true', dest= 'hash_en', help= 'Add arg -DTC_HASH_ENABLE for regression')
        parser.add_argument('--gkt', default = False, action = 'store_true', dest = 'gkt', help = 'Run gkt test')
    else:
        parser.add_argument('-n', default = False, action='store_true', dest= 'no_exe', help= 'Check command only')
        parser.add_argument('-f', '--func', default= 'theory', dest= 'func', help = 'functionality to call. \nValue: [theory|measure|check]')
        parser.add_argument('-e', '--edir', default= './', dest= 'edir', help = "The directory of where necessary files are existed. Under batch mode, it is the parent dir of all tests. Under single mode, it is concatenated with '-t' to locate the output.")
        parser.add_argument('-t', '--test', default= None, dest= 'test', help = 'regular expression test names, like "test\d+". By default it is all tests match test_ptn in testpm_cfg_d')
        parser.add_argument('-r', '--rdir', default= './', dest= 'rdir', help = "Reference test directory. Suggest using the parent directory of output of reference test")
        parser.add_argument('--cal', '--cal_value', default= None, dest= 'cal_value', help = "calculation value. eg. gemm_cal_value = 2*m*n*k. other ops need owner cal it yourself")
        parser.add_argument('--int', '--int', default= None, dest= 'int', help = "if element is int, you need add --int y ")
        parser.add_argument('--wpg', '--wpg', default= None, dest= 'wpg', help = "wpg: wave per group,4/8/16... eg. --wpg 4")
    options = parser.parse_args()

    return options

def get_labels(_2dict):
    """Get labels from 2D dict.
    Return: Max. collection of keys from every layer of dict
    """
    lb0 = list(_2dict.keys())
    lb1 = list()
    for k,v in _2dict.items():
        lb1.extend(list(v.keys()))
    return lb0, list(set(lb1))

def conv2df(_2dict):
    """Convert 2D dict to DataFrame
    Return: Column *ONLY* dataframe. Keys of layer-0 in _2dict \
    is unified as 1st column with keys from layer-1
    """
    from pandas import DataFrame as DF
    ##NOTE|Don't drop 'None' column
    _df = DF(_2dict).stack(dropna=False).unstack(0)
    ##move index to a column named 'name' for simplifying usage
    _df.insert(0,column='name',value=list(_df.index))
    _df = _df.reset_index(drop=True)
    ##Dealing column type to be the same one as the element in [0]
    for c in list(_df.columns):
        #NOTE|The 'None' is also converted into NaN(float64)
        if type(_df[c][0]) != str:
            _df[c] = _df[c].astype(float)
    return _df

def getna(_df, col='name'):
    '''Get the dataframe has 'NaN' from original dataframe
    A counterpart of dropna()
    '''
    ##Another way is using np.where to get index and column of 'nan' cell
    hasna = _df.loc[_df.isnull().any(1),:]
    return list(hasna[col]), hasna

def split_se_2df(se, symbol, out):
    """
    :se: an implicit parameter from apply()
    """
    df = DF()
    for k,v in se.items():
        #NOTE|join() can solve the variable length issue of new added columns
        #One series is splited into a dataframe per split symbol
        df = df.join(DF({k:str(v).split(symbol)}), how='right') 
    #NOTE|A workaround to solve the passing-in DataFrame couldn't be updated issue.
    #If use 'df' to pass a DF in and change it internally, use 'return df' is ok, but 
    #if this function is used in DataFrame.apply(), return a DF is not work well even 
    #with using reduce and broadcast options. The DF is mutable but looks like when use 
    #it as a paramter of a function, it's not a reference but a copy, to use a list or dict 
    #to workaround it XXX: Actually the simple way is to add 'return x' in function called in apply
    #see core_performance_theory.py:reunit
    out[0] = out[0].append(df, ignore_index=True)

def split_df(df, cols):
    '''
    :cols: 2D list as [[<columns of DF N>], ]
    '''
    df_l = []
    for cs in cols:
        df_l.append(df.loc[:,cs])
    return df_l

def get_now(which='dhms', delimiter=False):
      #[tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst]
    now= list(time.localtime())
    now= [str(i).zfill(2) for i in now] 
    def case(var):
        return {
            ('all', True): str(now[0]+'-'+now[1]+'-'+now[2]+'-'+now[3]+'-'+now[4]+'-'+now[5]),
            ('dhms', True): str(now[2]+'-'+now[3]+'-'+now[4]+'-'+now[5]),
            ('all', False): str(now[0]+now[1]+now[2]+now[3]+now[4]+now[5]),
            ('dhms', False): str(now[2]+now[3]+now[4]+now[5]),
            ('ymd', False): str(now[0][-2:]+now[1]+now[2])
        }.get(var, "[get_now]Wrong request")
    return case((which, delimiter))

from theory_util import *
from measure_util import *
from pmlog import PMLog
from pmgui import PMGui

if __name__=='__main__':
    #print(get_cfg_f(vg_cfg_f,False))
    #print(get_desc('kongming_ip','measure'))
    pass

