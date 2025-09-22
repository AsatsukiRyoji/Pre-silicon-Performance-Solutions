waive_list = {
    # below buffer ooo results based on the regression 05-10, which is confirmed by DE in JIRA743
    'perf_buffer_loadstorevalu_instruction_mtype_nc_ls_ooo_ON'  :
        {'ref_floor' : .0, 'ref_ceiling' : 10.0}
    ,'perf_buffer_loadstore_instruction_mtype_nc_ls_ooo_ON'  :
        {'ref_floor' : -0.05, 'ref_ceiling' : 10.0}
    ,'perf_buffer_loadstore_instruction_mtype_cc_ls_ooo_ON'  :
        {'ref_floor' : -0.05, 'ref_ceiling' : 10.0}
    # below global ooo results based on the regression 05-10, which is confirmed by DE in JIRA871
    ,'perf_global_loadstorevalu_instruction_mtype_nc_ls_ooo_ON'  :
        {'ref_floor' : .0, 'ref_ceiling' : 10.0}
    ,'perf_global_loadstore_instruction_mtype_nc_ls_ooo_ON'  :
        {'ref_floor' : -0.05, 'ref_ceiling' : 10.0}
    ,'perf_global_loadstore_instruction_mtype_cc_ls_ooo_ON'  :
        {'ref_floor' : -0.05, 'ref_ceiling' : 10.0}
    ,'perf_buffer_atomic_f32_ipw192_wpg4'  : 
        {'floor' : .66, 'ceiling' : .86}
    ,'perf_global_atomic_f32_ipw192_wpg4' : 
        {'floor' : .73, 'ceiling' : .93}
    # below global_load hit TCP results , which is confirmed by DE in JIRA1227
    ,'perf_global_load_dwordx1_toLDS_hitTCP_ipw64_wpg4_wrap\d+'  : 
        {'floor' : .79, 'ceiling' : .89}
    # below fullhash results based on the regression 05-04, which is confirmed by DE in JIRA642
    ,'perf_buffer_load_dwordx4_128B_hitTCC_ipw23_wpg4_fullhash_isize\d+' : 
        {'floor' : .63, 'ceiling' : .73}
    # below matrix_load to lds with ipw=4 results based on the regression 05-04, which is confirmed by DE in JIRA631
    ,'perf_matrix_load_b8_swON_r\w+_t\w+_ipw4_lds'                  : 
        {'floor' : .68, 'ceiling' : .78}
    ,'perf_matrix_load_b8_swOFF_rROW_tCOL_ipw4_lds'                  : 
        {'floor' : .76, 'ceiling' : .86}
    ,'perf_matrix_load_b8_swOFF_rCOL_tROW_ipw4_lds'                  : 
        {'floor' : .76, 'ceiling' : .86}
    ,'perf_matrix_load_b8_swOFF_rCOL_tCOL_ipw4_lds'                  : 
        {'floor' : .68, 'ceiling' : .78}
    ,'perf_matrix_load_b8_swOFF_rROW_tROW_ipw4_lds'                  :
        {'floor' : .68, 'ceiling' : .78}
    ,'perf_matrix_load_b16_sw\w+_r\w+_t\w+_ipw4_lds'                  : 
        {'floor' : .77, 'ceiling' : .87}
    # below matrix_load with ipw=4 results based on the regression 05-04, which is confirmed by DE in JIRA644
    ,'perf_matrix_load_b16_swON_rCOL_tROW_ipw4$'                     : 
        {'floor' : .79, 'ceiling' : .89}
    ,'perf_matrix_load_b16_swON_rROW_tCOL_ipw4$'                     : 
        {'floor' : .79, 'ceiling' : .89}
    # below global_load with wpg=2 results based on the regression 05-04, which is confirmed by DE in JIRA586
    ,'perf_global_load_dwordx1_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .60, 'ceiling' : .70}
    ,'perf_global_load_dwordx1_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .62, 'ceiling' : .72}
    ,'perf_global_load_dwordx1_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .63, 'ceiling' : .73}
    ,'perf_global_load_dwordx1_toLDS_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .60, 'ceiling' : .70}
    ,'perf_global_load_dwordx1_toLDS_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .62, 'ceiling' : .72}
    ,'perf_global_load_dwordx1_toLDS_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .63, 'ceiling' : .73}
    # below buffer store results based on the regression 01-04, which is confirmed by DE in JIRA513
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw32_wpg2'                    : 
        {'floor' : .70, 'ceiling' : .90}
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw48_wpg2'                    : 
        {'floor' : .68, 'ceiling' : .88}
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw48_wpg4'                    : 
        {'floor' : .71, 'ceiling' : .91}
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw48_wpg8'                    : 
        {'floor' : .70, 'ceiling' : .90}
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw64_wpg2'                    : 
        {'floor' : .75, 'ceiling' : .95}
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .70, 'ceiling' : .90}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .71, 'ceiling' : .91}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw32_wpg4'                   : 
        {'floor' : .75, 'ceiling' : .95}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .63, 'ceiling' : .83}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .57, 'ceiling' : .77}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .69, 'ceiling' : .89}
    ,'perf_buffer_store_dwordx2_comp1_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .51, 'ceiling' : .71}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .73, 'ceiling' : .93}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .67, 'ceiling' : .87}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .58, 'ceiling' : .78}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .70, 'ceiling' : .90}
    ,'perf_buffer_store_dwordx2_comp2_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .53, 'ceiling' : .73}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .69, 'ceiling' : .89}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw32_wpg4'                   : 
        {'floor' : .58, 'ceiling' : .78}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .44, 'ceiling' : .64}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .64, 'ceiling' : .84}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .53, 'ceiling' : .73}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .43, 'ceiling' : .63}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .66, 'ceiling' : .86}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .42, 'ceiling' : .62}
    ,'perf_buffer_store_dwordx4_comp1_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .38, 'ceiling' : .58}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .70, 'ceiling' : .90}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw32_wpg4'                   : 
        {'floor' : .60, 'ceiling' : .80}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .44, 'ceiling' : .64}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .67, 'ceiling' : .87}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .48, 'ceiling' : .68}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .38, 'ceiling' : .58}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .61, 'ceiling' : .81}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .43, 'ceiling' : .63}
    ,'perf_buffer_store_dwordx4_comp2_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .38, 'ceiling' : .58}
    ,'perf_buffer_store_dwordx1_comp1_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .74, 'ceiling' : .94}
    # above buffer store results based on the regression 01-04, which is confirmed by DE in JIRA513

    #update below global store results based on the regression 02-21, which is confirmed by DE in JIRA514
    ,'perf_global_store_dwordx1_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .69, 'ceiling' : .89}
    ,'perf_global_store_dwordx1_hitTCC_ipw32_wpg4'                   : 
        {'floor' : .74, 'ceiling' : .94}
    ,'perf_global_store_dwordx1_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .73, 'ceiling' : .93}
    ,'perf_global_store_dwordx1_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .67, 'ceiling' : .87}
    ,'perf_global_store_dwordx1_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .71, 'ceiling' : .91}
    ,'perf_global_store_dwordx1_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .70, 'ceiling' : .90}
    ,'perf_global_store_dwordx1_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .73, 'ceiling' : .93}
    ,'perf_global_store_dwordx1_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .75, 'ceiling' : .95}
    ,'perf_global_store_dwordx1_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .61, 'ceiling' : .81}

    ,'perf_global_store_dwordx2_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .71, 'ceiling' : .91}
    ,'perf_global_store_dwordx2_hitTCC_ipw32_wpg4'                   : 
        {'floor' : .73, 'ceiling' : .93}
    ,'perf_global_store_dwordx2_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .68, 'ceiling' : .88}
    ,'perf_global_store_dwordx2_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .72, 'ceiling' : .92}
    ,'perf_global_store_dwordx2_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .70, 'ceiling' : .90}
    ##specially ten percent up and low limits##
    ,'perf_global_store_dwordx2_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .58, 'ceiling' : .78}
    ###########################################
    ,'perf_global_store_dwordx2_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .71, 'ceiling' : .91}
    ##specially ten percent up and low limits##
    ,'perf_global_store_dwordx2_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .65, 'ceiling' : .85}
    ,'perf_global_store_dwordx2_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .52, 'ceiling' : .72}
    ###########################################

    ,'perf_global_store_dwordx4_hitTCC_ipw32_wpg2'                   : 
        {'floor' : .68, 'ceiling' : .88}
    ,'perf_global_store_dwordx4_hitTCC_ipw32_wpg4'                   : 
        {'floor' : .57, 'ceiling' : .77}
    ,'perf_global_store_dwordx4_hitTCC_ipw32_wpg8'                   : 
        {'floor' : .45, 'ceiling' : .65}
    ,'perf_global_store_dwordx4_hitTCC_ipw48_wpg2'                   : 
        {'floor' : .65, 'ceiling' : .85}
    ##specially ten percent up and low limits##
    ,'perf_global_store_dwordx4_hitTCC_ipw48_wpg4'                   : 
        {'floor' : .47, 'ceiling' : .67}
    ###########################################
    ,'perf_global_store_dwordx4_hitTCC_ipw48_wpg8'                   : 
        {'floor' : .43, 'ceiling' : .63}
    ,'perf_global_store_dwordx4_hitTCC_ipw64_wpg2'                   : 
        {'floor' : .65, 'ceiling' : .85}
    ##specially ten percent up and low limits##
    ,'perf_global_store_dwordx4_hitTCC_ipw64_wpg4'                   : 
        {'floor' : .40, 'ceiling' : .60}
    ###########################################
    ,'perf_global_store_dwordx4_hitTCC_ipw64_wpg8'                   : 
        {'floor' : .40, 'ceiling' : .60}
}


