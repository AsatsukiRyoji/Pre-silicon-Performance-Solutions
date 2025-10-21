#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enforce sync the tree every 6 hour, easy to get the build or simulation sanity changlist, for only_run_one_gc_build_sim_tree
@author: Guo Shihao
Data: 2025.04.18
"""
import os, re, sys, logging, subprocess, time, argparse, pdb

logging.basicConfig(filename='/project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_info.log', level=logging.INFO)
cdir = os.path.dirname(os.path.realpath(__file__)) + '/'

parting_line = '''
###################################
'''
blank_line = '''


'''
### original cmd
#dj_cmd = ('lsf_bsub -Ip -q regr_high dj -c -e 'run_test"perf perf_buffer_load_dwordx4_toLDS_comp1_hitTCC_ipw32_wpg4_so0_tid0"' -m 200 -l /project/hawaii/a0/arch/archpv/%s/logs/perf_buffer_load_dwordx4_toLDS_comp1_hitTCC_ipw32_wpg4.log -DGC_PERF -DSKIP_CAT_EMU_VEC ')
### removed arg: 
dj_cmd = ('/tool/pandora64/bin/lsf_bsub -Ip -q regr_high dj -e \'run_test "cs/cs_sr_sanity_pm4_01"\' -DRUN_GC_SIM -DGFX_CGCG_ENABLE -DGFX_MGCG_ENABLE -DGC_ENABLE_LLVM_SP3 -l /project/hawaii/a0/arch/archpv/%s/logs/cs_sr_sanity_pm4_01_build.log -DFSDB_RUNTIME_CTRL -DDUMP_WAVE_WITH_LIBFILE -DDUMP_ITRACE -DRUN_DV=OFF')
dj_cmd_sim = ('/tool/pandora64/bin/lsf_bsub -Ip -q regr_high dj -e \'run_test "cs/cs_sr_sanity_pm4_01"\' -DRUN_GC_SIM -DGFX_CGCG_ENABLE -DGFX_MGCG_ENABLE -l /project/hawaii/a0/arch/archpv/%s/logs/cs_sr_sanity_pm4_01_sim.log -DFSDB_RUNTIME_CTRL -DDUMP_WAVE_WITH_LIBFILE -DDUMP_ITRACE -DRUN_DV=ONLY')
dj_cmd_sim_1 = ('/tool/pandora64/bin/lsf_bsub -Ip -q regr_high dj -e \'run_test "cs/cs_queue_dispatch_pm4_02"\' -DRUN_GC_SIM -DGFX_CGCG_ENABLE -DGFX_MGCG_ENABLE -l /project/hawaii/a0/arch/archpv/%s/logs/cs_aql_dispatch_pm4_01.log -DFSDB_RUNTIME_CTRL -DDUMP_WAVE_WITH_LIBFILE -DDUMP_ITRACE -DRUN_DV=ONLY')
ptb_cmd_sim_sanity = ('bsub -W 6:00 -Ip -q regr_high $STEM/out/compile/cache_sanity_test/simv -l ./verdi_run.log +vcs+lic+wait -assert verbose+errmsg -assert nopostproc +seed=94540070 +ntb_random_seed=94540070 +tb_period=10ns -reportstats +UVM_TR_RECORD +UVM_LOG_RECORD -assert global_finish_maxfail=1000000 +dyn_gpr_mgmt_enabled +UVM_TESTNAME=cache_sanity_test +testname=%s +dump_addr=0x11000000 +dump_size=0x8000000 +UVM_TIMEOUT=600000000 +UVM_VERBOSITY=UVM_MEDIUM +UVM_VERDI_TRACE=UVM_AWARE+RAL+TLM+TLM2+IMP+HIER +all_drivers=off +fsdbFileSize=2500 +pc0_pc1_interp_tracker=off +pc1_pc0_interp_tracker=off +pc2_pc3_interp_tracker=off +pc3_pc2_interp_tracker=off +pc_pc_read_tracker=off +set_values_seed=94540070 +spi_sq_cmd_monitor=on +sq_spi_msg_monitor=on +spi_sq_cmd_tracker=off +UVM_OBJECTION_TRACE +UVM_PHASE_TRACE +all_monitors=on %s ')

def option_parser(type=None):
    parser = argparse.ArgumentParser(description='%s options' %type, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--tree', default= 'only_run_one_gc_build_sim_tree', dest= 'tree',  help= 'Choose which tree you run')
    options = parser.parse_args()  
    return options

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

def get_now(which='dhms', delimiter=False):
      #[tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst]
    now= list(time.localtime())
    now= [str(i).zfill(2) for i in now] 
    def case(var):
        return {
            ('all', True): str(now[0]+'/'+now[1]+'/'+now[2]+' '+now[3]+':'+now[4]+':'+now[5]),
            ('dhms', True): str(now[2]+' '+now[3]+'-'+now[4]+'-'+now[5]),
            ('all', False): str(now[0]+now[1]+now[2]+now[3]+now[4]+now[5]),
            ('dhms', False): str(now[2]+now[3]+now[4]+now[5])
        }.get(var, "[get_now]Wrong request")
    return case((which, delimiter))

def cmd_crontab(stable_tree):
    os.chdir('/project/hawaii/a0/arch/archpv/' + stable_tree + '/') # change the directory and print the time
    logging.info(parting_line + 'Start at:  ' + get_now('all', True) + parting_line)
    logging.info(os.getcwd())
    #call_from_sys('setenv P4CONFIG P4CONFIG')
    with open('P4CONFIG', 'r') as file:
        for line in file:
            port_name, port_content = line.strip().split('=')
            os.environ[port_name] = port_content
    ### Sync the tree
    logging.info(' ##########  This is sync ... ##########')
    sync_info = subprocess.getoutput('p4 sync -f ...')  # sync tree
    #logging.info(sync_info)
    logging.info(' ##########  Sync done ... ##########')
    call_from_sys('rm -rf /project/hawaii/a0/arch/archpv/'+ stable_tree + '/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/pub/sim/exec/*')
    call_from_sys('rm -rf /project/hawaii/a0/arch/archpv/'+ stable_tree + '/out/linux_3.10.0_64.VCS/vega20c/config/gc_perf/pub/sim/vcs.work/*')
    ### Update the changelist
    changes = os.popen('p4 changes -m 1').read()
    ptn = r'(Change )(\d+)'
    changelist = re.search(ptn, changes).groups()[1]
    open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/configuration_id','w').write(changelist)
    logging.info('The current changelist is:' + changelist)
    ### Run the dj cmd
    #dj_cmd_info = subprocess.getoutput(dj_cmd)    # rerun the test
    #logging.info(dj_cmd_info)
    dj_cmd_new = dj_cmd%(stable_tree)
    result, status = call_from_sys(dj_cmd_new, has_status=True)
    #logging.info('sanity_status:' + str(status))
    #open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/result_crontab_delete', 'w').write(str(result))
    #open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/status_crontab_delete', 'w').write(str(status))
    sanity_status = result[result.index('failed_cmd_count:') + 1]
    logging.info('Build status:' + sanity_status)
    # open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/sanity_status', 'w').write(sanity_status)
    dj_cmd_new = dj_cmd_sim_1%(stable_tree)
    result, status = call_from_sys(dj_cmd_new, has_status=True)
    try:
        sanity_status_sim = result[result.index('failed_cmd_count:') + 1]
    except:
        sanity_status_sim = 'Not Simulation Pass'
    logging.info('Simulation status:' + sanity_status_sim)
    open('/project/hawaii/a0/arch/archpv/' + stable_tree + '/sanity_status', 'w').write(sanity_status)
    logging.info(' ##########  End  ##########')
    logging.info(blank_line)


if __name__=='__main__':
    opt = option_parser()
    cmd_crontab(opt.tree)


