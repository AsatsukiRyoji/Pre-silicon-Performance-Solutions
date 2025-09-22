#!/usr/bin/env python3
import os, re
import sys
import subprocess
import itertools
from typing import Dict, List, Optional, Any
from regression.prun_regr_base import prunRegrBase
from utility import util

class prunRegrSystem(prunRegrBase):
    """GKT regression testing system"""
    def __init__(self):
        """Initialize GKT regression system"""
        super().__init__()
        self.stem = os.environ.get('STEM', '')
        self.gkt_root = os.environ.get('GKT_ROOT', '')
        if not self.stem:
            raise ValueError("STEM environment variable not set")
        self.gkt_regr_dir = os.path.join(self.stem, 'regression')
        
        # Initialize performance configuration
        self.perf_config = {
            'collect_perf': False,
            'compare_golden': False
        }

        # Initialize test lists
        self.lists = {
            'bowen_b0_ip': 'perf_bowen_b0_ip.testlist',
            'run_again': 'perf_run_again.testlist'
        }
    
    def test_postproc(self, test_name: str) -> None:
        """Run post-processing for a test
        
        Args:
            test_name: Name of the test
        """
        try:
            # Get output directory
            out_dir = self._get_output_dir(test_name)
            
            # Load test processor
            processor = self._load_test_processor(test_name)
            if processor is None:
                self._update_results(test_name, 'ERROR', error='Failed to load test processor')
                return
                
            # Run basic checks
            status = processor.run_checks(out_dir)
            error = processor.get_error() if not status else ''
            
            # Collect and compare performance metrics if enabled
            if self.perf_config['collect_perf']:
                metrics = self.collect_performance_metrics(test_name)
                if metrics and self.perf_config['compare_golden']:
                    self.compare_with_golden(test_name, metrics)
                    
            # Update results
            self._update_results(
                test_name,
                'PASS' if status else 'FAIL',
                error=error
            )
            
        except Exception as e:
            self._update_results(test_name, 'ERROR', error=str(e))
            
    def _get_output_dir(self, test_name: str) -> str:
        """Get GKT test output directory
        
        Args:
            test_name: Name of the test
            
        Returns:
            Path to test output directory
        """
        return os.path.join(self.gkt_root, 'gkt_out', test_name)
    
    def run_regr(self, desc: str, regr: str, mode: str = 'normal',
                 no_build: bool = False, exe: str = '', dump: bool = False,
                 hash_en: bool = False, gui_en: bool = False) -> None:
        """Run regression tests
        
        Args:
            desc: Description file path
            regr: Regression configuration
            mode: Run mode ('normal', 'postproc', etc.)
            no_build: Skip build if True
            exe: Path to executable
            dump: Enable dump if True
            hash_en: Enable hash if True
            gui_en: Enable GUI if True
        """
        # Store configuration
        self.desc = desc
        self.regr = regr
        self.mode = mode
        self.no_build = no_build
        self.exe = exe
        self.dump = dump
        self.hash_en = hash_en
        self.gui_en = gui_en
        
        self.build_needed = not no_build
        self.postproc_only = (mode == 'postproc')
        
        # Configure performance regression
        if mode in ['perf', 'performance']:
            self.perf_config['collect_perf'] = True
            self.perf_config['compare_golden'] = True
        
        # Setup environment
        if not self.setup_env():
            print("Failed to setup environment")
            return
            
        # Build if needed
        if self.build_needed:
            if not self._build():
                print("Build failed")
                return
                
        # Get test list
        if self.desc:
            list_file = os.path.join(self.gkt_regr_dir, self.lists.get(self.desc, ''))
            if not os.path.exists(list_file):
                print(f"Test list file not found: {list_file}")
                return
            test_ptn = self.get_test_ptn(list_file)

        if not self.test_list:
            self.gen_tests('command', test_ptn)
        # Configure run mode
        self._configure_run_mode()
        
        # Configure additional options
        self._configure_options()

        # Generate test list based on description
        
        # Run tests
        all_tests = [test for tests in self.test_list.values() 
                    for test in tests]
        self.async_engine(all_tests)
        
        # Print summary
        self._print_summary()
        
    def run_gkt_regress(self, mode: str, tests: List[str]) -> bool:
        """Run GKT regression command
        
        Args:
            mode: Mode ('golden', 'run', or 'compare')
            tests: List of tests to run
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Change to GKT regression directory
            curr_dir = os.getcwd()
            os.chdir(self.gkt_regr_dir)
            
            # Build command
            cmd = ['python3', 'gkt_regress.py', f'--mode={mode}']
            cmd.extend(tests)
            
            # Run command
            result = subprocess.run(cmd, 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
            
            os.chdir(curr_dir)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error running GKT regression: {e}")
            if 'curr_dir' in locals():
                os.chdir(curr_dir)
            return False
            
    def setup_env(self) -> bool:
        """Setup GKT environment
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Set environment variables
            os.environ['GKT_ROOT'] = self.gkt_root
            os.environ['PYTHONPATH'] = os.pathsep.join([
                os.environ.get('PYTHONPATH', ''),
                self.gkt_root
            ])
            return True
        except Exception as e:
            print(f"Error setting up environment: {e}")
            return False
            
    def _build(self) -> bool:
        """Build GKT regression
        
        Returns:
            True if build successful, False otherwise
        """
        return super()._build()
        #try:
        #    cmd = ['make', '-C', self.gkt_root]
        #    result = subprocess.run(cmd,
        #                         stdout=subprocess.PIPE,
        #                         stderr=subprocess.PIPE,
        #                         text=True)
        #    return result.returncode == 0
        #except Exception as e:
        #    print(f"Build failed: {e}")
        #    return False
            
    def _configure_run_mode(self) -> None:
        """Configure test run mode"""
        if self.postproc_only:
            print("Running in post-processing only mode")
        else:
            print(f"Running tests with {self.parallel_jobs} parallel jobs")
            
    def _configure_options(self) -> None:
        """Configure additional run options"""
        # Set up executable if provided
        if self.exe:
            os.environ['GKT_EXE'] = self.exe
            
        # Configure dump option
        if self.dump:
            os.environ['GKT_DUMP'] = '1'
            
        # Configure hash option
        if self.hash_en:
            os.environ['GKT_HASH'] = '1'
            
        # Configure GUI option
        if self.gui_en:
            os.environ['GKT_GUI'] = '1'
            
    def enum_pattern_manual(self, pattern):
        # 1. 找出所有简单分组，不支持嵌套
        groups = re.findall(r'\(([^)]+)\)', pattern)
        # 2. 将 A|B|C 形式拆分为 ['A','B','C']
        options = [grp.split('|') for grp in groups]
        # 3. 把每个分组替换成占位符 {}
        template = re.sub(r'\([^)]*\)', '{}', pattern)
        # 4. 生成笛卡尔积并填入模板
        combos = [''.join(item) for item in
                  (template.format(*combo) for combo in itertools.product(*options))]
        return combos

    def enum_pattern_(self, pattern):
        # 1. 找出所有简单分组，不支持嵌套
        groups = re.findall(r'\(([^)]+)\)', pattern)

        # 2. 将 A|B|C 形式拆分为 ['A','B','C']
        options = [grp.split('|') for grp in groups]

        # 3. 把每个分组替换成占位符 {}
        template = re.sub(r'\([^)]*\)', '{}', pattern)

        # 4. 手动实现笛卡尔积
        def cartesian_product(lists):
            result = [[]]
            for pool in lists:
                new_result = []
                for prefix in result:
                    for item in pool:
                        new_result.append(prefix + [item])
                result = new_result
            return result

        combos = [''.join(template.format(*combo)) for combo in cartesian_product(options)]
        return combos
  
    def gen_tests(self, domain=None, pattern=None):
        tests = []
        if domain is not None:
            for k,v in pattern[domain].items():
                for group in v:
                    combos = self.enum_pattern_(group)
                    if 'spi' in group:
                        tests.extend(combos)
                        for combo in combos:
                            #os.system(f"python3 ./test/spi.py --output --debug -n {combo}")
                            print(f"gen {combo} done")
                    elif 'cp' in group:
                        tests.extend(combos)
                        for combo in combos:
                            #os.system(f"python3 ./test/cpdc_aql_dispatch.py --output --debug -n {combo}")
                            print(f"gen {combo} done")
                    else:
                        print(f"Unknown group: {group}")
        return tests
    #def gen_test(self, desc: str) -> None:
    #    """Generate test list based on description"""
    #    if not self.desc:
    #        print("No description file provided")
    #        return
    #        
    #    try:
    #        with open(self.desc, 'r') as f:
    #            desc_data = json.load(f)
    #            self.test_list = desc_data.get('tests', {})
    #    except Exception as e:
    #        print(f"Error reading description file: {e}")
    #        self.test_list = {}
            
    def _run_simulation(self, test_name: str) -> bool:
        """Run GKT simulation
        
        Args:
            test_name: Name of the test
            
        Returns:
            True if simulation successful, False otherwise
        """
        return self.run_gkt_regress('run', [test_name])
        
    def _get_output_dir(self, test_name: str) -> str:
        """Get GKT test output directory
        
        Args:
            test_name: Name of the test
            
        Returns:
            Path to test output directory
        """
        return os.path.join(self.gkt_root, 'gkt_out', test_name)
        
    def _get_golden_dir(self) -> str:
        """Get GKT golden results directory
        
        Returns:
            Path to golden results directory
        """
        return os.path.join(self.gkt_root, 'gkt_out', 'golden')
        
    def _load_test_processor(self, test_name: str) -> Any:
        """Load GKT test processor
        
        Args:
            test_name: Name of the test
            
        Returns:
            GKT test processor object
        """
        try:
            # First try loading performance test processor
            if self.perf_config['collect_perf']:
                perf_proc = self._load_perf_processor(test_name)
                if perf_proc:
                    return perf_proc
                    
            # Fall back to standard test processor
            module_name = f"test.{test_name}"
            module = __import__(module_name, fromlist=['TestProcessor'])
            return module.TestProcessor()
            
        except Exception as e:
            print(f"Error loading test processor for {test_name}: {e}")
            return None
            
    def _load_perf_processor(self, test_name: str) -> Any:
        """Load GKT performance test processor
        
        Args:
            test_name: Name of the test
            
        Returns:
            GKT performance processor object
        """
        try:
            # Try loading from testpm module
            module_name = f"methodology.testpm.{test_name}_pm"
            class_name = f"{test_name.title()}PM"
            
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)()
            
        except Exception as e:
            print(f"Error loading performance processor for {test_name}: {e}")
            return None
            
    def _print_summary(self) -> None:
        """Print regression test summary"""
        total = len(self.results_df)
        passed = len(self.results_df[self.results_df['Status'] == 'PASS'])
        failed = len(self.results_df[self.results_df['Status'] == 'FAIL'])
        errors = len(self.results_df[self.results_df['Status'] == 'ERROR'])
        
        print("\nRegression Test Summary:")
        print(f"Total Tests  : {total}")
        print(f"Passed      : {passed}")
        print(f"Failed      : {failed}")
        print(f"Errors      : {errors}")
        
        if failed > 0 or errors > 0:
            print("\nFailed/Error Tests:")
            failed_tests = self.results_df[
                self.results_df['Status'].isin(['FAIL', 'ERROR'])
            ]
            for _, row in failed_tests.iterrows():
                print(f"{row['TestName']}: {row['Status']} - {row['ErrorMsg']}")
                
if __name__ == '__main__':
    opt = util.option_parser('regression')
    regr = prunRegrSystem()
    
    # 运行性能回归测试
    regr.run_regr(
        desc=opt.desc,         # 测试描述文件
        regr=opt.regr,        # 回归配置
        mode='perf',          # 性能回归模式
        no_build=opt.no_build,
        exe=opt.exe,
        dump=opt.dump,
        hash_en=opt.hash_en,
        gui_en=opt.gui_en
    )

#if __name__ == "__main__":
#    opt = util.option_parser('regression')
#    regr = prunRegrSystem()
#    regr.run_regr(opt.desc, opt.regr, opt.mode, opt.no_build, opt.exe, opt.dump, opt.hash_en, opt.gui_en)