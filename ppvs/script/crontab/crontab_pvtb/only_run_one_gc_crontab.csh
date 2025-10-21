#!/bin/tcsh
### for only_run_one_gc_build_sim_tree
date >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log
source ~/.cshrc
source /project/hawaii/a0/arch/archpv/crontab/crontab_pvtb/eda_modulefile
cd /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/
set current_date = `date +%Y-%m-%d`
#inicbwa
#bootenv_
    ## for xcd, use source to do inicbwa and bootenv
source /toolkit/hyvmt/verif_release_ro/cbwa_initscript/1.0.0/_init.csh 
source /toolkit/hyvmt/verif_release_ro/cbwa_bootcore/$bootcore_ver/bin/_bootenv.csh -o /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/out.$current_date
echo "/project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/out.$current_date"
#echo /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/out.$current_data >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log
#echo "aa$current_data" >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log
date >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log
echo "environment done" >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log

#@ content_pvtb_sanity_tree_run_mynumber = $content_pvtb_sanity_tree_run
apy /project/hawaii/a0/arch/archpv/crontab/crontab_pvtb/only_run_one_gc_tree.py -t only_run_one_gc_build_sim_tree
set content_pvtb_sanity_tree_status = `cat /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/sanity_status`
echo "only_gc_one_tree_status:"  $content_pvtb_sanity_tree_status >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log
echo '... End ...' >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log
echo '' >> /project/hawaii/a0/arch/archpv/only_run_one_gc_build_sim_tree/crontab_csh.log

