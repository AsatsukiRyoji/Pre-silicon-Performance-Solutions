## Project illustration (PVM methodology around perf_test_pm.py)

### Overview
- **Entry class**: `methodology/testpm/perf_test_pm.py` defines `PerfTestPM` with three flows: `theory`, `measure`, `check`.
- **Core modules**:
  - Theory: `methodology/theory/core_performance_theory.py` (`ComputeCoreTheory`)
  - Measure: `methodology/measure/core_performance_measure.py` (`ComputeCoreMeasure`) with helpers in `methodology/measure/measure_lib/*` and `methodology/utility/measure_util.py`
  - Check: `methodology/check/core_performance_check.py` (`ComputeCoreCheck`) and `methodology/check/test_performance_check.py` (CLI wrapper that writes CSV)
  - GUI: `methodology/utility/pmgui.py` (`PMGui`)
  - Common utils/config: `methodology/utility/util.py` (desc/config parsing, GUI helper), `methodology/methodology.cfg` plus per-project `desc/*.cfg`

### High-level data flow
1) Theory
   - Derived PMs build a `meta_df` from test configs, then:
     ```70:74:methodology/testpm/perf_lds_vmem_pm.py
     cct = CCT(desc,meta_df)
     self.theo = cct.get_theory()
     ```
   - `ComputeCoreTheory.get_theory()` computes columns, bottleneck, unit; it does not write CSV itself.

2) Measure
   - Base `PerfTestPM.measure` collects test metadata and execution dirs, then:
     ```68:76:methodology/testpm/perf_test_pm.py
     ccm = CCM(desc, meta_df)
     _df = ccm.get_measure()
     ```
   - `ComputeCoreMeasure.get_measure()` invokes algorithms from `measure_lib/*` and `measure_util.py`, returning a DataFrame; some algorithms also write helper CSVs in the execution dir (see below).

3) Check
   - `PerfTestPM.check` calls theory+measure, merges result columns, then:
     ```118:126:methodology/testpm/perf_test_pm.py
     ccc = CCC(desc, chk_df)
     chk_df = ccc.get_chk(is_ref, algo, is_latency)
     self.chk_df = chk_df
     ```
   - `methodology/check/test_performance_check.py` writes the final CSV for a test:
     ```219:225:methodology/check/test_performance_check.py
     f = edir+'/'+test+'_perf_check_result.csv'
     pm.chk_df.to_csv(f, mode='w')
     ```

### Q1. How CSVs are calculated and written in theory, measure, and check modes
- **Theory mode**
  - Calculation: `ComputeCoreTheory.get_theory()` computes theoretical throughput/latency metrics and bottlenecks in-memory.
    ```198:206:methodology/theory/core_performance_theory.py
    def get_theory(self):
        for k,v in cct_func_keys.items():
            ...
            eval(fn)(vld)
    ```
  - Writing: No built-in CSV write in theory core (no `to_csv` here). You can persist `self.theo` manually if needed.

- **Measure mode**
  - Calculation: `ComputeCoreMeasure.get_measure()` dispatches to specific algorithms; results assembled into `self.meas` DataFrame.
  - Writing: Some measurement helpers write CSV artifacts into the execution directory:
    - Shader latency summaries:
      ```768:775:methodology/measure/measure_lib/shader_measure.py
      ave_file_path = edir + 'average_L1_L2_latency.csv'
      with open(ave_file_path, mode='w', newline='') as ave_f:
          writer = csv.writer(ave_f)
      ```
    - Channel request ratio:
      ```827:840:methodology/utility/measure_util.py
      csv_path = edir + 'channel_req_ratio.csv'
      writer = csv.DictWriter(csvfile, fieldnames=column_name, delimiter='\t')
      ```
    - Various debug/merge tables via `DataFrame.to_csv("...")` during analysis:
      ```1418:1497:methodology/measure/measure_lib/shader_measure.py
      merge_df_data.to_csv("merge_df_data")
      tag_latency.to_csv("tag_latency")
      ```
    - Batch quick-measure summary:
      ```104:106:methodology/quickm.py
      with open(cdir + '/all_test_algo_result.csv', 'w' ) as f:
          df_all_test.to_csv(f)
      ```

- **Check mode**
  - Calculation: `ComputeCoreCheck.get_chk()` compares theory vs measure and produces `check` and `ratio` columns.
  - Writing: The canonical output CSV is written by the check wrapper:
    ```219:225:methodology/check/test_performance_check.py
    f = edir+'/'+test+'_perf_check_result.csv'
    pm.chk_df.to_csv(f, mode='w')
    ```

- [Checkpoint-1] Answered: CSV behavior per theory/measure/check identified with sources and file names.

### Q2. Where does the GUI’s displayed data come from?
- GUI is fed by in-memory pandas DataFrames passed to `PMGui.run()`:
  - Measure flow GUI:
    ```77:80:methodology/testpm/perf_test_pm.py
    if gui_en:
        gui = util.PMGui()
        gui.run([self.meas])
    ```
  - Check flow GUI:
    ```123:126:methodology/testpm/perf_test_pm.py
    if gui_en:
        gui = util.PMGui()
        gui.run([self.chk_df])
    ```
  - GUI implementation renders the given DataFrame(s):
    ```117:153:methodology/utility/pmgui.py
    def run(self, df_l, cols=[]):
        ...
        for d in ds:
            ... _tvw.insert('','end',values=d.loc[i,:].tolist())
    ```
- `PMGui.show()` is a separate convenience to load a CSV from disk into a DataFrame and then call `run()`, but the perf flows use the in-memory path.

- [Checkpoint-2] Answered: GUI reads directly from `self.theo`/`self.meas`/`self.chk_df` DataFrames passed into `PMGui.run()`.

### Q3. Can the data shown in GUI mode be printed to a CSV file?
- **Yes.** There are two practical options without modifying existing code:
  - Use existing writer where available:
    - For check results, run the wrapper that already saves CSV: `test_performance_check.py` writes `<edir>/<test>_perf_check_result.csv`.
  - Or persist the same DataFrames used for GUI:
    - Theory: save `self.theo`
    - Measure: save `self.meas`
    - Check: save `self.chk_df` (if you didn’t use the check wrapper)
    Example (Python):
    ```python
    from methodology.testpm.perf_test_pm import PerfTestPM
    ptpm = PerfTestPM()
    ptpm.measure(desc='bowen_b0_ip', algo='spisq_launch', edir='./out/', test='your_test', gui_en=True)
    ptpm.meas.to_csv('measure_gui_view.csv', index=False)
    ```
    You can do the same for `ptpm.theo` and `ptpm.chk_df` after their respective calls.

- [Checkpoint-3] Answered: Feasible to export GUI data to CSV via `DataFrame.to_csv(...)` or by running the existing check wrapper.

### Minimal project map (relevant to perf_test_pm.py)
- `methodology/testpm/perf_test_pm.py`: Orchestrates theory/measure/check and optional GUI display.
- `methodology/theory/core_performance_theory.py`: Theory calculations; returns DataFrame `theo`.
- `methodology/measure/core_performance_measure.py`: Measurement aggregation; returns DataFrame `meas`; helpers in `measure_lib/*`, `utility/measure_util.py` may write CSV artifacts.
- `methodology/check/core_performance_check.py`: Check/ratio computation over merged theory+measure DataFrame `chk_df`.
- `methodology/check/test_performance_check.py`: CLI that calls check and writes `<test>_perf_check_result.csv` under the test’s output dir.
- `methodology/utility/pmgui.py`: Tkinter GUI; renders passed DataFrame(s).
- `methodology/utility/util.py`: CLI options, config loading, glue utilities.

### Thinking log (brief)
- Mapped `perf_test_pm.py` imports and read core modules for theory/measure/check and GUI.
- Grepped for `.csv` writes to identify exactly where files are generated; confirmed measure helpers and check wrapper write CSV; theory core does not.
- Traced GUI data path to `PMGui.run()` showing it consumes in-memory DataFrames produced by the flows.
- Confirmed feasibility of exporting the same DataFrames with `to_csv()` without changing existing code.


