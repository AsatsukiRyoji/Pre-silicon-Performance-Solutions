#!/bin/tcsh
source ~/.cshrc
source /project/hawaii/a0/arch/archpv/crontab/crontab_pvtb/eda_modulefile
cd /project/hawaii/a0/arch/archpv/shader/
set current_date = `date +%Y%m%d`
date >> /project/hawaii/a0/arch/archpv/shader/shader_crontab_csh.log
echo "Build PTB Tree:" shader_sanity_ptb_$current_date >> /project/hawaii/a0/arch/archpv/shader/shader_crontab_csh.log
apy /project/hawaii/a0/arch/guoshihao/git_pvtb/pvtb/script/ptb_tree_manage.py -t /project/hawaii/a0/arch/archpv/shader/shader_sanity_ptb_$current_date --new
source /project/hawaii/a0/arch/archpv/shader/shader_sanity_ptb_$current_date/pvtb/env_dir.sh
cd /project/hawaii/a0/arch/archpv/shader/shader_sanity_ptb_$current_date/
cp -r /project/hawaii/a0/arch/archpv/shader/mls_test/matrix_load_32x16_b16_hitTCC_sw0_r0_t0_alt0_bps0_ipw4_wpg4_lds /project/hawaii/a0/arch/archpv/shader/shader_sanity_ptb_$current_date/pvtb/src/test/sanity/
run_ptb.py -flow cs -t shader_sanity --dump_fsdb --backdoor_sh_mem_enable 
run_ptb.py -flow s -t matrix_load_32x16_b16_hitTCC_sw0_r0_t0_alt0_bps0_ipw4_wpg4_lds --dump_fsdb --backdoor_sh_mem_enable 
echo '... End ...' >> /project/hawaii/a0/arch/archpv/shader/shader_crontab_csh.log

