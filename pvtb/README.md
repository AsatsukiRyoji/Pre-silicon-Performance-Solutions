# Cache Regression Directory Structure

This directory contains the complete cache regression framework as described in the `cache_regression_instructions.md` file.

## Directory Structure
```
ptb_vitual
├── configuration_id
├── out
│   ├── compile
│   └── run
└── src
    ├── design
    │   ├── libaray
    │   │   └── lib_xx
    │   ├── misc
    │   ├── rtl
    │   │   └── block_xx
    │   └── shell
    ├── gkt
    ├── model
    │   ├── core_soc_model
    │   ├── lib_mdl
    │   └── soc_model
    ├── ptb
    │   ├── debug
    │   │   ├── lib_so
    │   │   ├── monitors
    │   │   └── trace
    │   ├── include
    │   ├── misc
    │   ├── model_apater
    │   ├── sequence
    │   ├── test
    │   └── uvc
    ├── pvm
    ├── scripts
    │   ├── README.md
    │   ├── compile
    │   ├── env_dir.sh
    │   ├── flow
    │   ├── run
    │   └── utils
    ├── shell
    │   └── library
    │       └── lib_name
    └── stimuli
        ├── isa
        │   ├── bandwidth
        │   └── sanity
        └── opr
            └── sanity
```

## Key Files

### Environment Configuration
- `pvtb/env_dir.sh`: Sets up environment variables and paths

### Compilation
- `pvtb/vcs_compile_psm.run_bwc`: VCS compilation script for cache sanity test

### Test Generation
- `pvtb/src/gkt/shells/select_and_run_gen.py`: Generates test files based on patterns

### Performance Analysis
- `pvtb/src/methology/testpm/prun_isa_pm.py`: Analyzes performance metrics

### Test Files
- `pvtb/src/test/cache_sanity_test.sv`: Basic cache functionality test
- `pvtb/src/test/cache_tb.sv`: Cache testbench
- `pvtb/src/test/testlist.txt`: Test list with patterns

## Usage

1. **Set up environment**:
   ```bash
   source pvtb/env_dir.sh
   ```

2. **Run cache regression**:
   ```bash
   python regression/cache_performance_regression.py -l pvtb/src/test/testlist.txt -r cache_regression_001
   ```

3. **Compile project**:
   ```bash
   bsub pvtb/vcs_compile_psm.run_bwc
   ```

4. **Generate test**:
   ```bash
   apy pvtb/src/gkt/shells/select_and_run_gen.py test_name
   ```

5. **Check performance**:
   ```bash
   apy pvtb/src/methology/testpm/prun_isa_pm.py -f check -e $STEM/out_path/run -f testname
   ```

## Test Patterns

The testlist supports patterns like:
- `cache_perf_test(128|256|512)`: Expands to 3 separate tests
- `buffer_load_ipw(128|64)_wpg(4)_dwpi(1|2|4)_comp(1)_hit(TCC)`: Expands to 6 combinations

## Performance Metrics

Performance tests generate CSV files with metrics like:
- Request/response ratios
- Channel utilization
- Cache hit rates
- Timing statistics

The framework automatically checks for 'pass' status in these files to determine test success.
