#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance methodology theory specific utility
@author: Li Lizhao
"""

from util import *

def parse_dv(dv):
    if os.path.isfile(dv):
        parsed = call_from_sys('m4 '+dv)
    elif type(dv)==str and not dv.endswith('dv'):
        parsed = [dv]
    else:
        print( "%s is not a file" %(dv))
        sys.exit()
    return parsed

def get_test_info(test_ptn, param_l, parsed):
    """get test info.
    :test_ptn: Input. Can be a list of pattern or single str pattern
    :parsed: list of a single test name or a listed translated dv file
    :RETURN: OrderedDict {test name: key info}
    """
    test_d= OrderedDict()
    ptn_l= [test_ptn] if type(test_ptn)!= list else test_ptn
    #if type(parsed) is str:
    #    for ptn in ptn_l:
    #        if re.search(r''+ptn+'', parsed):
    #            _grps= (re.search(r''+ptn+'', parsed)).groups()
    #            test_d[parsed]= _grps
    #else:
    for l in parsed:
        ##[XXX]Put this 'ptn' loop inside has better performance 
        for ptn in ptn_l: 
            if re.search(r''+ptn+'', l):
                _tn = (re.search(r''+ptn+'', l)).group(0)
                if _tn.endswith(':'):
                    _tn = _tn.strip(':')
                if _tn.startswith(' '):
                    _tn = _tn.strip(' ')
                _grps = (re.search(r''+ptn+'', _tn)).groups()
                param = list()
                for i,v in enumerate(_grps):
                    try:
                        #[XXX]Don't use 'eval', it might turn some words into <built-in function (name)>, like 'all'
                        param.append(int(v))
                    except:
                        param.append(v)
                #[XXX]Don't try to convert str to other types since not sure what user wants
                test_d[_tn]= OrderedDict(zip(param_l,param))
    return test_d

def get_test_desc(dv, ptn, param_l):
    '''
    dv: single dv file or a list
    '''
    dv_l = [dv] if type(dv) != list else dv
    test_d= OrderedDict()
    for dv in dv_l:    
        parsed = parse_dv(dv)
        test_d.update(get_test_info(ptn, param_l, parsed))
    return test_d

def acquire_all_tests(cfg, test=None, type='theory'):
    """Common function to acquire all tests
    :dv: dv file with abs. dir 
    :test: reg-ex of test name
    """
    test_info_df = conv2df(get_test_desc(cfg['dv'], cfg['test_ptn'], cfg['test_param_l']))
    #pdb.set_trace()
    if test != None:  
        test_info_df = test_info_df.set_index(test_info_df['name'])
        tests = list(test_info_df['name'])
        tests = [t for t in tests if re.search(r''+test+'', t)]
        test_info_df=test_info_df.loc[tests,:]
        #reset index to serial number
        test_info_df.reset_index(drop=True, inplace=True)
    if type=='measure':
        return DF(test_info_df['name'])
    else:
        return test_info_df

if __name__ == '__main__':
    pass

