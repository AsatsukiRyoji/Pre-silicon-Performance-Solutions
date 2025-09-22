#!/usr/bin/env python3
import os, re
import sys
import json
import subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any

class prunRegrBase:
    """Base class for regression testing system"""
    
    def __init__(self):
        """Initialize regression system with default settings"""
        # LSF command configuration
        self.lsf_cmd = {
            'bsub': 'bsub',
            'queue': '-q normal',
            'resources': '-R "rusage[mem=4096]"'
        }
        
        # DJ command configuration
        self.dj_cmd = {
            'base': 'dj',
            'options': '--batch'
        }

        # vcs compile options
        self.compile = {
            'vcs': {
                'vcs_options': '+error+4 -sverilog',
                'uvm_options': 'uvm-1.2 -lca -full64',
                'debug_options': '-debug_access+all -MMD -MV -kdb',
                'assert_options': '-assert novpd+dbsopt',
                'stats_options': '-reportstats -top tb',
                'options': '-full64',
                'define': '+define+COSIM_LIB_UNAVAILABLE +define+SYSTEM/ptb/cmodel +define+PTBTB_BMC +define+PVTB_CP_SHELL +define+SOC_MODEL',
                'include': '-I $SYSTEM/out/compile -I $SYSTEM/out/cmodel -I $SYSTEM/ptb/src',
                'libraries': '-lstdc++ -lm',
                'flags': '-sverilog -vecio_pli -P $SYSTEM/src/rtcp/vecio.tab',
                'coverage': '-Xloopopt=amd1',
                'key_options': '-Xkeyopt=amd1',
            },
            'verilator': {
                'options': '--cc --exe --build',
                'define': '-DVERILATOR -DVERILATOR_SIM'
            }
        }

        # simulation
        self.sim = {
            'timing': {
                'period': '+tb_period=10ms',
                'timeout': '+UVM_TIMEOUT=50000000000'
            },
            'reporting': {
                'stats': '+reportstats',
                'verbosity': '+assert verboserrmsg',
                'max_fail': '+assert global_finish maxfail=1000000'
            },
            'uvm_trace': {
                'tr_record': '+UVM_TR_RECORD +UVM_LOG_RECORD',
                'objection': '+UVM_OBJECTION_TRACE',
                'phase': '+UVM_PHASE_TRACE',
                'resource': '+UVM_RESOURCE_DB_TRACE'
            },
            'debug': {
                'nopostsim': '+assert nopostsim',
                'seed': '+seed=94540070'
            },
            'performance': {
                'dyn_perf': '+mgmt_perf_enabled +UVM_TESTNAME=cache_sanity',
                'cache_size': '+dump_size=11000000',
                'trackers': {
                    'c3_interp': '-c3_interp_tracker=off',
                    'pc3_pc2': '+pc3_pc2_interp_tracker=off',
                    'pc_pc': '+pc_pc_read_tracker=off',
                    'pc0_pci': '+pc0_pci_interp_tracker=off',
                    'pci': '+pci_pc0_interp_tracker=off'
                },
                'monitoring': {
                    'spi_cmd': '+spi_sq_cmd_monitor=on',
                    'spi_msg': '+sq_spi_msg_monitor=on',
                    'tracker': '+spi_cmd_tracker=off'
                }
            },
            'features': {
                'fall_drive': '+fall_drive=off',
                'buffer_size': '+tsdbFileSiz=2500'
            }
        }
        
        # DV options
        self.dv_options = {
            'simulator': 'vcs',
            'coverage': False,
            'debug': False
        }
        
        # Test related data
        self.test_list = {}
        self.results_df = pd.DataFrame(columns=[
            'TestName', 'TestGroup', 'Status', 
            'SimTime', 'CovRate', 'ErrorMsg'
        ])
        
        # Performance regression related data
        self.perf_results = pd.DataFrame(columns=[
            'TestName', 'TestGroup', 'MetricName',
            'Measured', 'Expected', 'Tolerance',
            'Status', 'Comment'
        ])
        
        # Configuration
        self.perf_config = {
            'collect_perf': True,    # Whether to collect performance metrics
            'compare_golden': True,  # Whether to compare with golden results
            'tolerances': {          # Default tolerances for different metrics
                'latency': 0.05,     # 5% tolerance for latency
                'bandwidth': 0.10,   # 10% tolerance for bandwidth
                'throughput': 0.08   # 8% tolerance for throughput
            }
        }
        
        # Additional control options
        self.desc = ''           # Description file path
        self.regr = ''          # Regression configuration
        self.mode = 'normal'    # Run mode
        self.no_build = False   # Skip build flag
        self.exe = ''           # Executable path
        self.dump = False       # Enable dump
        self.hash_en = False    # Enable hash
        self.gui_en = False     # Enable GUI
        
        # Runtime configuration
        self.build_needed = False
        self.postproc_only = False
        self.parallel_jobs = os.cpu_count() or 4
        
    def get_test_ptn(self, flist: str) -> Dict[str, Any]:
        """Read and parse test configuration file
        
        Args:
            test_list: Path to test list
            
        Returns:
            Dictionary containing test configuration
        """
        try:
            ptn = {}
            # Read test configuration file
            with open(flist, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):

                        # Parse test category if in brackets
                        match = re.match(r'\[(\w+)\]', line)
                        if match:
                            domain = match.group(1)
                            ptn[domain.lower()] = {}
                            continue

                        # Parse test group and subgroup
                        if '=' in line:
                            group, subgroup = [x.strip() for x in line.split('=', 1)]
                            if group and subgroup:
                                ptn[domain.lower()][group] = subgroup.split()
                            continue
            return ptn
        except Exception as e:
            print(f"Error reading test config file: {e}")
            return {}
            
    def setup_env(self) -> bool:
        """Setup runtime environment
        
        Returns:
            True if setup successful, False otherwise
        """
        # Add implementation in derived class
        return True

    def _build(self, queue=None, test=None, exe=False) -> bool:
        """Build GKT regression
        
        Returns:
            True if build successful, False otherwise
        """
        try:
            cmd = self.lsf_cmd['bsub'].split()

            if queue is not None:
                cmd += ['-q', str(queue)]
            else:
                cmd += self.lsf_cmd['queue'].split()

            if test is not None:
                cmd += [test]
            else:
                cmd += self.lsf_cmd['resources'].split()

            # Add compile options based on simulator
            comp_options = []
            if self.dv_options['simulator'] == 'vcs':
                compile_opts = self.compile['vcs']
                for key, value in compile_opts.items():
                    if isinstance(value, str):
                        comp_options.extend(value.split())

            elif self.dv_options['simulator'] == 'verilator':
                compile_opts = self.compile['verilator']
                for key, value in compile_opts.items():
                    if isinstance(value, str):
                        comp_options.extend(value.split())

            cmd.extend(comp_options)

            if exe:
                result = subprocess.run(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
                #print(f"Output: {result.stdout}")
                #print(f"Errors: {result.stderr}")
                return result.returncode == 0
            else:
                print(cmd)
                return True
        except Exception as e:
            print(f"Build failed: {e}")
            return False
            
    async def async_engine(self, test_list: List[str]) -> None:
        """Asynchronous test execution engine
        
        Args:
            test_list: List of tests to execute
        """
        with ThreadPoolExecutor(max_workers=self.parallel_jobs) as executor:
            futures = []
            for test in test_list:
                future = executor.submit(self.sim_and_postproc, test)
                futures.append(future)
                
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Test execution failed: {e}")
                    
    def sim_and_postproc(self, test_name: str) -> None:
        """Run simulation and post-processing for a test
        
        Args:
            test_name: Name of the test to run
        """
        if not self.postproc_only:
            # Run simulation
            status = self._run_simulation(test_name)
            if not status:
                self._update_results(test_name, 'FAIL', error='Simulation failed')
                return
                
        # Run post-processing
        self.test_postproc(test_name)
        
    def test_postproc(self, test_name: str) -> None:
        """Post-process test results
        
        Args:
            test_name: Name of the test to process
        """
        try:
            # Get output directory
            out_dir = self._get_output_dir(test_name)
            
            # Load test processor
            processor = self._load_test_processor(test_name)
            
            # Run checks
            status = processor.run_checks(out_dir)
            
            # Update results
            self._update_results(
                test_name,
                'PASS' if status else 'FAIL',
                error=processor.get_error() if not status else ''
            )
            
        except Exception as e:
            self._update_results(test_name, 'ERROR', error=str(e))
            
    def _run_simulation(self, test_name: str) -> bool:
        """Run simulation command
        
        Args:
            test_name: Name of the test to simulate
            
        Returns:
            True if simulation successful, False otherwise
        """
        # Add implementation in derived class
        return True
        
    def _get_output_dir(self, test_name: str) -> str:
        """Get output directory for test
        
        Args:
            test_name: Name of the test
            
        Returns:
            Path to test output directory
        """
        # Add implementation in derived class
        return ''
        
    def _load_test_processor(self, test_name: str) -> Any:
        """Load test processor for post-processing
        
        Args:
            test_name: Name of the test
            
        Returns:
            Test processor object
        """
        # Add implementation in derived class
        return None
        
    def _update_results(self, test_name: str, status: str, 
                       sim_time: float = 0.0, cov_rate: float = 0.0,
                       error: str = '') -> None:
        """Update results dataframe
        
        Args:
            test_name: Name of the test
            status: Test status (PASS/FAIL/ERROR)
            sim_time: Simulation time
            cov_rate: Coverage rate
            error: Error message if any
        """
        test_group = next((g for g, tests in self.test_list.items() 
                          if test_name in tests), '')
        
        new_row = pd.DataFrame([{
            'TestName': test_name,
            'TestGroup': test_group,
            'Status': status,
            'SimTime': sim_time,
            'CovRate': cov_rate,
            'ErrorMsg': error
        }])
        
        self.results_df = pd.concat([self.results_df, new_row], 
                                  ignore_index=True)
                                  
    def collect_performance_metrics(self, test_name: str) -> Dict[str, float]:
        """Collect performance metrics for a test
        
        Args:
            test_name: Name of the test
            
        Returns:
            Dictionary containing performance metrics
        """
        metrics = {}
        output_dir = self._get_output_dir(test_name)
        
        try:
            # Load test specific performance processor
            processor = self._load_perf_processor(test_name)
            if processor:
                metrics = processor.collect_metrics(output_dir)
        except Exception as e:
            print(f"Error collecting performance metrics for {test_name}: {e}")
            
        return metrics
        
    def compare_with_golden(self, test_name: str, 
                           metrics: Dict[str, float]) -> None:
        """Compare performance metrics with golden results
        
        Args:
            test_name: Name of the test
            metrics: Dictionary of collected metrics
        """
        if not metrics:
            return
            
        test_group = next((g for g, tests in self.test_list.items() 
                          if test_name in tests), '')
        golden_file = os.path.join(self._get_golden_dir(), 
                                 f"{test_name}_golden.json")
                                 
        try:
            if os.path.exists(golden_file):
                with open(golden_file, 'r') as f:
                    golden_metrics = json.load(f)
                    
                for name, value in metrics.items():
                    tolerance = self.perf_config['tolerances'].get(
                        self._get_metric_type(name), 0.05)
                    expected = golden_metrics.get(name)
                    
                    if expected is not None:
                        status = 'PASS'
                        comment = ''
                        if abs(value - expected) > expected * tolerance:
                            status = 'FAIL'
                            comment = (f"Deviation {abs(value-expected)/expected:.2%} "
                                     f"exceeds tolerance {tolerance:.2%}")
                                     
                        self._update_perf_results(
                            test_name, test_group, name,
                            value, expected, tolerance, status, comment
                        )
                        
        except Exception as e:
            print(f"Error comparing with golden results for {test_name}: {e}")
            
    def _get_metric_type(self, metric_name: str) -> str:
        """Get the type of a performance metric
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Type of the metric (latency, bandwidth, or throughput)
        """
        if any(x in metric_name.lower() for x in ['latency', 'delay', 'time']):
            return 'latency'
        elif any(x in metric_name.lower() for x in ['bandwidth', 'bw']):
            return 'bandwidth'
        elif any(x in metric_name.lower() for x in ['throughput', 'iops']):
            return 'throughput'
        return 'default'
        
    def _update_perf_results(self, test_name: str, test_group: str,
                            metric_name: str, measured: float,
                            expected: float, tolerance: float,
                            status: str, comment: str) -> None:
        """Update performance results dataframe
        
        Args:
            test_name: Name of the test
            test_group: Group of the test
            metric_name: Name of the metric
            measured: Measured value
            expected: Expected value
            tolerance: Tolerance percentage
            status: Test status (PASS/FAIL)
            comment: Additional comment
        """
        new_row = pd.DataFrame([{
            'TestName': test_name,
            'TestGroup': test_group,
            'MetricName': metric_name,
            'Measured': measured,
            'Expected': expected,
            'Tolerance': tolerance,
            'Status': status,
            'Comment': comment
        }])
        
        self.perf_results = pd.concat([self.perf_results, new_row],
                                    ignore_index=True)
                                    
    def _load_perf_processor(self, test_name: str) -> Any:
        """Load performance processor for a test
        
        Args:
            test_name: Name of the test
            
        Returns:
            Performance processor object
        """
        try:
            # Import performance processor dynamically
            module_name = f"testpm.{test_name}_pm"
            processor_name = f"{test_name.title()}PM"
            
            module = __import__(module_name, fromlist=[processor_name])
            return getattr(module, processor_name)()
            
        except Exception as e:
            print(f"Error loading performance processor for {test_name}: {e}")
            return None
            
    def _get_golden_dir(self) -> str:
        """Get directory containing golden results
        
        Returns:
            Path to golden results directory
        """
        # Add implementation in derived class
        return ''
