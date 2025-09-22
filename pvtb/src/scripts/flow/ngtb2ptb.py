class PVTBTree()
    def __init__(self):
        self.i, self.j = 2,2
        self.project = ""
        self.shell_list = []
        self.shell_sub_module_list = []
        self.cmt_sv_list = []
        self.cmt_specific_list = []
        self.maint_file_list = []
        self.rtl_map = {}
        self.incdir_map = {}
        self.cmt_instance ={        }
        self.rtl2shell_def_list = []
        self.cmt_module ={}
        self.cp_single_replace = ""
        self.vec_specified_files =[        ]
        self.copy, self.error,self.skip
        self.incdir_files,self.all_files,self.relative_include = [],{},{}
        self.reduced_files_set = set()
        self.all_files_set_g, self.all_files_set_filename = set(), set()
        self.all_files_set_v, self.all_files_set_v_filename， self.only_include_files = set(), set(), set()
        self.all_files_list_sum, slef.all_files_list_sum_ = [],[]
        self.abandon_file_suffix = []
        self.ngtb_base_dir_list = []
        self.pvtb_tab_file_list = []

    
if __name__ == "__main__":
    pt = PVTBTree()
    opt = pt.option_parser()
    flist = opt.flist 
    start_time time.time()
    pt.exec_func_precise(flist)
    used_time = time.time() - start_time
