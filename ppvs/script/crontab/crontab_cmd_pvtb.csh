#!/bin/tcsh

date >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
source ~/.cshrc
source /project/hawaii/a0/arch/archpv/crontab/eda_modulefile
#cd /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/
#inicbwa
#bootenv_
date >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
echo "environment done" >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
#tool/pandora64/bin/python3 /project/hawaii/a0/arch/archpv/pvtb_stable_tree_crontab.py          # build status, please check build log
set content_pvtb_sanity_tree_status = `cat /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/sanity_status`
set content_sanity_backup_tree_status = `cat /project/hawaii/a0/arch/archpv/pvtb_sanity_tree_backup/sanity_status`
set content_pvtb_sanity_tree_run = `cat /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/whether_run_flag`
set content_sanity_backup_tree_run = `cat /project/hawaii/a0/arch/archpv/pvtb_sanity_tree_backup/whether_run_flag`
echo "Tree1_status:"  $content_pvtb_sanity_tree_status >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
echo "Tree2_status:"  $content_sanity_backup_tree_status >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
echo "Tree1_run:" $content_pvtb_sanity_tree_run >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
echo "Tree2_run:" $content_sanity_backup_tree_run >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log

#@ content_pvtb_sanity_tree_run_mynumber = $content_pvtb_sanity_tree_run
if ($content_pvtb_sanity_tree_run == "had_run") then   #if tree1 had_run, clean the flag
    echo "tree1 run flag:" $content_pvtb_sanity_tree_run >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
    sed -i 's/had_run/have_not_run/g' /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/whether_run_flag  # clear tree1 run flag
    #if ($content_pvtb_sanity_tree_status == '0' || $content_pvtb_sanity_tree_status == '1') then  #if tree1 had pass, run tree2
    if ($content_pvtb_sanity_tree_status == '0') then  #if tree1 had pass, run tree2
        echo "... Tree2_status:"  $content_sanity_backup_tree_status >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        echo "... Tree2 Run ..."  >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        cd /project/hawaii/a0/arch/archpv/pvtb_sanity_tree_backup/
        inicbwa
        bootenv_
        python3 /project/hawaii/a0/arch/archpv/crontab/pvtb_stable_tree_crontab.py -t pvtb_sanity_tree_backup
    else  #if tree1 had_run but have_not_pass, continue run tree1
        echo "... Tree1_status:" $content_pvtb_sanity_tree_status >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        echo "... Tree1 Run ..."  >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        cd /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/
        inicbwa
        bootenv_
        python3 /project/hawaii/a0/arch/archpv/crontab/pvtb_stable_tree_crontab.py -t pvtb_sanity_tree
    endif
else  # if tree1 have_not_run, and if tree2 passed last time, run tree1 now
    #if ($content_sanity_backup_tree_status == '0' || $content_sanity_backup_tree_status == '1') then # tree2 passed last time, clean tree2 run_flag, run tree1 now
    if ($content_sanity_backup_tree_status == '0') then # tree2 passed last time, clean tree2 run_flag, run tree1 now
        echo "... Tree1_status:" $content_pvtb_sanity_tree_status >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        echo "... Tree1 Run ..."  >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        cd /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/
        inicbwa
        bootenv_
        python3 /project/hawaii/a0/arch/archpv/crontab/pvtb_stable_tree_crontab.py -t pvtb_sanity_tree
    else
        echo "... Tree2_status:"  $content_sanity_backup_tree_status >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        echo "... Tree2 Run ..."  >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
        cd /project/hawaii/a0/arch/archpv/pvtb_sanity_tree_backup/
        inicbwa
        bootenv_
        python3 /project/hawaii/a0/arch/archpv/crontab/pvtb_stable_tree_crontab.py -t pvtb_sanity_tree_backup
    endif
endif
echo '... End ...' >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log
echo '' >> /project/hawaii/a0/arch/archpv/pvtb_sanity_tree/crontab_csh.log

