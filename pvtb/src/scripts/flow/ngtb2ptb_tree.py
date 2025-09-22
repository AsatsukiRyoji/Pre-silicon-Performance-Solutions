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

    def flist_for_copy(self,flist,cp_out_flist, old_few_incdir,more):
        pass
    
    def get_now(self, which='dhms', delimiter=False):
        pass
    
    def change_path2stem(self, src_flist, target, more):
        pass
    
    def gen_rtl_f(self,target,rtl_src,inc_src,old_few_incdir):
        pass
    
    def gen_rtl_f_1(self, target, inc_src, rtl_src):
        pass
    
    def copy2file(self, target, src_file, target_file):
        pass
    
    def get_incdir_filter_2copy(self, target, line, reduced_files, incdir_all_flist):
        pass
    
    def get_rtl_filter_2copy(self, target, line, rtl_flag):
        pass
    
    def mpp_path_flist(self, source_flist, target_flist, target, reduced_flist, incdir_all_flist,more):
        pass
    
    def flist_delete_cmt(self, target, flist, ngtb_all_cmt_flist, rtl_target, more):    
        pass

    def copy_rtl_files(self, flist, target_dir, preserve_structure = True, more = True):
        pass

    def get_incdir(self, line, out_target):
        pass
    
    def copy_incdir(self, flist,target,more):
        pass
    
    def create_folder(self, target):
        pass
    
    def copy_one_path(self, src_dir, tar_dir, more):
        pass
    
    def tab_flist_only_copy(self, ngtb_base_dir, target, appended_flist, more):
        pass
    
    def relative_include_copy(self,target):
        pass

    def ngtb_v_inc_only_copy(self,target,src_flist,ngtb_base_dir):
        pass

    def flist_change_shell(self,ngtb_base_dir,target, filename,last_flist,reduced_flist,appended_flist,more):
        pass

    def appended_files_from_source_to_flist(self,ngtb_base_dir,ngtb_rtl_cmt_flist,last_rtl_flist):
        pass
    
    def parse_flist(self,filelist_path):
        pass

    def find_include_file(self,include_name,current_file_dir,inc_dirs,ngtb_base_dir)\
        pass

    def extract_includes(self, file_path):
        pass
    
    def get_include_file(self, target, src_flist, out_flist, ngtb_base_dir):
        pass
    
    def flist_cmt_sub_module(self,target,source_flist,reduced_flist):
        pass
    
    def only_get_rtl_and_cmt_flist(self, target, src_flist, rtl_out_flist,cmt_v_flist):
        pass
    
    def maintain_file2shell(self, file_path, shell_list):
        pass

    def file_repalce_lines(self,target,more):
        pass

    def file_cmt_lines(self,target,more):
        pass

    def gen_makef(self,target,more):
        pass
    
    def monitor_delete(self,target,more):
        pass

    def rm_tree_dir(self,target):
        pass

    def rm_one_file(self, file_dir):
        pass

    def copy_one_file(self, src_dir, target_dir):
        pass

    def copy_config_id(self , src_dir, target):
        pass

    def change_pvtb_env(self, target, more):
        pass

    def cpc_shell_maintain(self,src_dir,target):
        pass

    def print_maintain(self,target):
        pass

    def write_all_copy_files(self,target):
        pass

    def get_git(self, target, key, one_git, more)
        pass

    def gen_git(self, target):

    def original_flist(self, target):
        pass
    
    def reduc_append_to_last_rtl_flist():
        pass
    
    def last_mmp_for_copy_flist():
        pass

    def get_flist():
        pass
    
    def shell_config():
        pass
    
    def details_maintain():
        pass
    
    def exec_func_precise():
        pass
    
    def option_parser(self,type = None):
        pass
    
    def get_flist_dir(self):
        pass
    
if __name__ == "__main__":
    pt = PVTBTree()
    opt = pt.option_parser()
    flist = opt.flist 
    start_time time.time()
    pt.exec_func_precise(flist)
    used_time = time.time() - start_time
