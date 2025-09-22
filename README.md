# Pre-silicon-Performance-Solutions

## PVTB (Pre-silicon Verification Test Bench) 目录结构

以下是 `PVTB` 目录的结构总结，主要用于验证环境：

-   `configuration_id`: PTB 根目录，Perforce CL (Change List) 相关。
-   `src`: PTB 源代码目录。
    -   `design`: 设计目录。
        -   `rtl`: 包含各种 `<block>` 的 RTL 代码，例如 `atc`, `cp`, `f32`, `gc`, `gds`, `grbm`, `lds`, `rlc`, `shared`, `sp`, `spi`, `sq`, `sqc`, `sx`, `ta`, `tc`, `tcp`, `tcr`, `td`, `tpi`。
        -   `shell`: Shell 脚本目录。
        -   `library`: 库文件目录，包含 `<lib_name>`，例如 `address`, `atcl2`, `dft`, `dftmisc`, `ea`, `rsmu`, `rtllib`, `utcl2`, `vml2`。
        -   `misc`: 未分类文件。
    -   `ptb`: PTB 验证环境目录。
        -   `include`: 包含文件。
        -   `sequence`: 序列文件。
        -   `test`: 测试文件。
        -   `uvc`: UVC (Universal Verification Component) 相关文件。
        -   `debug`: 调试相关目录。
            -   `lib_so`: 动态链接库文件。
            -   `monitors`: Monitor 文件。
            -   `trace`: Trace 文件。
        -   `model_apater`: Model 对应的 PTB 接口。
        -   `misc`: 未分类文件。
    -   `model`: 模型目录。
        -   `lib_mdl`: Model 库。
        -   `soc_model`: 单 Die 模型，用于 Cosim (协同仿真)，稳定后会被多 Die 模型合并。
        -   `core_soc_model`: 多 Die 模型，用于 Cosim。
    -   `stimuli`: 测试用例目录。
        -   `isa`: ISA (Instruction Set Architecture) 相关的测试。
            -   `sanity`: 健全性测试。
            -   `bandwidth`: 带宽测试。
        -   `opr`: 操作相关的测试。
            -   `sanity`: 健全性测试。
    -   `scripts`: PTB Flow 及命令文件目录。
        -   `README.md`: 命令指南。
        -   `flow`: PTB Flow 脚本。
        -   `utils`: PTB 辅助脚本。
        -   `env_dir.sh`: 仿真工具及环境变量设置。
        -   `compile`: 编译命令和 filelist。
        -   `run`: 仿真命令和 dump 设置。
    -   `gkt`: GenKT 目录。
    -   `pvm`: PVM 目录。
-   `out`: 输出文件目录。
    -   `compile`: 编译输出。
    -   `run`: 运行输出。