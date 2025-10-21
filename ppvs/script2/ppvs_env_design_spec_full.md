# PVTB 环境自动化搭建系统设计文档

## 1. 引言

本文档旨在描述一个新的 PVTB (Pre-Silicon Verification Test Bench) 环境自动化搭建系统的设计。该系统将整合当前 `flow_filelist.md` 中描述的所有功能和流程，并通过一个统一的命令行接口为最终用户提供简化的环境搭建体验。此外，系统将增强对维护者的可调试性，并引入通过指定 Perforce changelist (CL) 号来获取特定 NGTB RTL 代码的新功能。

## 2. 目标

新系统的主要目标包括：

1.  **功能继承**：完全继承 `flow_filelist.md` 中定义的所有 PVTB 环境搭建功能和特性。
2.  **单命令操作**：最终用户可以通过执行一个简洁的命令行指令，完成整个 PVTB 环境的自动化搭建。
3.  **可维护性与可调试性**：为系统维护者提供清晰、详细的日志输出和流程信息，方便快速定位和调试问题。
4.  **Changelist 指定**：允许用户在搭建环境时，通过指定 Perforce CL 号来获取对应 NGTB 环境的 RTL 代码，实现版本控制的灵活性。
5.  **环境类型区分与独立脚本**：将 PVTB 环境搭建拆分为两个独立的脚本，分别用于 `pvtb_developer` 和 `ppvs` 环境，明确各自的特性与功能。
    *   **`pvtb_developer` (内部开发者环境)**：使用 `ngtb2pvtb_tree_manage.py` 脚本，具备完整的 PVTB 功能，不对外可见，仅限内部使用。将通过专用脚本 `ppvs_env_setup_developer` 进行搭建。
    *   **`ppvs` (外部用户环境)**：使用 `ngtb2ptb_tree_manage_new.py` 脚本，目录结构与 `pvtb_developer` 有所差异，并会删除部分 PVTB 功能，提供精简版。将通过专用脚本 `ppvs_env_setup_user` 进行搭建。

## 3. 现有功能与特性 (继承自 `flow_filelist.md`)

新系统将整合并自动化以下现有流程和脚本的功能。其中，`/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/p4client_manage.py` 脚本将被完全复用。其余在 `flow_filelist.md` 中提及的脚本，其核心功能和逻辑将作为可复用的组件被新系统直接调用，或根据需要进行封装和适配。系统将根据所选的环境类型 (`pvtb_developer` 或 `ppvs`) 进行适配：

### 3.1 Crontab 定时任务相关逻辑
1.  **Crontab 定时任务触发**：
    *   **入口点**: 定时任务执行 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/crontab_cmd_pvtb_tree.csh`。其核心逻辑将被新系统的 NGTB 处理模块直接调用或封装。
    *   **环境初始化**: `crontab_cmd_pvtb_tree.csh` `source ~/.cshrc` 和 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/eda_modulefile` 设置 shell 和 EDA 工具环境。相关环境初始化逻辑将被集成到新系统，并直接复用或封装。
    *   **状态检查与决策**: `crontab_cmd_pvtb_tree.csh` 读取 `simulation_sanity_status` 和 `whether_run_flag` 等状态文件，决定运行哪个 PVTB 树（故障转移或交替执行）。此状态管理与决策逻辑将被直接复用并集成到新系统内部。

2.  **Perforce 客户端管理 (如果尚未设置或需要更新)**：
    *   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/p4client_manage.py` 将被直接复用，用于创建 Perforce 客户端、同步初始代码并生成 `P4CONFIG` 文件。在自动化流程中，通常假设客户端已存在并配置好。

3.  **PVTB 环境搭建与代码转换**：
    *   **主要执行者**: `crontab_cmd_pvtb_tree.csh` 调用 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/pvtb_stable_copy_tree_crontab.py`。其核心功能（NGTB Perforce 同步、Makefile 修改、hbo 构建等）将被新系统的 NGTB 处理模块直接调用或封装。
        *   **NGTB 环境内文件修改**：`pvtb_stable_copy_tree_crontab.py` 在 NGTB 环境中进行以下关键文件修改：
            *   **Perforce 文件签出** (`ngtb_tree_run` 函数)：使用 `p4 edit` 命令签出需要修改的核心文件，包括 `src/verif/sh/tools/cmn/Makefile` 和 `src/verif/sh/tools/cmn/sh_itrace.cpp`，确保文件可编辑。
            *   **Makefile 修改** (`change_cmn_makefile` 函数)：在 `src/verif/sh/tools/cmn/Makefile` 的 `LLFLAGS` 行前添加注释标记 ` # PPVS: Added library flags for PVTB compatibility`，并追加链接库标志 `LLFLAGS += -L$(OUT_CMN_bin) -lmemio -lsp3 -lsp3_disasmble -lsh_meta`，为后续 PVTB 编译提供必要的库链接。
            *   **sh_itrace.cpp 修改** (`change_cmn_itrace` 函数）：
                *   在 `#include <math.h>` 行后追加 `#include <string.h>\n#include <stdarg.h>\n`，补充缺失的标准库头文件
                *   对包含头文件 `#include <medusa.h>`、`#include <sysmgr/sysmgr.h>`、`#include <sysmgr/filelog.h>` 的行添加 `//pvtb//` 前缀注释，禁用这些系统管理器相关的头文件包含
                *   在 `sysmgr data` 相关行（约18行）前添加 `//pvtb//` 前缀注释，禁用系统管理器数据处理功能，确保代码在 PVTB 环境中正常运行
            *   **hbo 构建执行** (`after_change_hbo` 函数）：在修改文件后自动执行 hbo 构建命令，通过 pexpect 与 tcsh shell 交互，依次执行环境初始化（`source _init.csh` 和 `source _bootenv.csh`）和 hbo 构建，验证修改后的环境是否能正常构建。
            *   **构建产物备份** (`ngtb_tree_run` 函数）：在构建前将现有的输出目录备份为 `out.last.bak`，确保构建失败时可以回滚。
    *   **构建状态检查**：脚本通过检查特定路径下的编译产物 (`vcs_sim_exe`) 来判断构建是否成功，如果构建产物不存在则将 `sanity_status` 设置为 '1' 表示构建失败。
    *   **Changelist 记录**：获取最新的 Perforce changelist 号并写入 `configuration_id` 文件，用于跟踪代码版本和变更历史。
    *   **PVTB 树复制与编译**：如果 NGTB 构建通过，将根据环境类型调用相应的脚本 (`ngtb2pvtb_tree_manage.py` 或 `ngtb2ptb_tree_manage_new.py`/`ngtb2ptb_tree_manage_precise.py`) 复制 NGTB 树到 PVTB 目标树，并进行 PVTB 的编译。这些脚本的核心逻辑将被 PVTB 转换模块直接调用或封装。针对 `ppvs` 环境，会根据需要删除部分功能。
        *   **Git 仓库管理**：克隆/更新 `pvtb` 仓库。此功能将被直接复用或封装。
        *   **目录结构创建**：根据 PVTB 环境要求创建必要的目录结构，`pvtb_developer` 和 `ppvs` 的目录结构将有所差异。此功能将被直接复用或封装。
        *   **Flist 处理**：处理 `verdi_with_vcs.f` 文件列表（路径转换）。此功能将被直接复用或封装。
        *   **文件复制与转换**：复制 RTL 文件、include 目录，并进行文件内容替换（例如针对 `cp.v`）。此功能将被直接复用或封装。
        *   **Shell 模块替换与修改**：对核心 RTL 文件进行“shell”化修改。此功能将被直接复用或封装。
        *   **宏定义修改**：调整宏定义。此功能将被直接复用或封装。
        *   **C-shell 文件修改**：修改 C-shell 文件。此功能将被直接复用或封装。
        *   **配置文件复制**：复制 `configuration_id` 和其他维护文件。此功能将被直接复用或封装。
        *   **环境变量更新**：更新 `pvtb/env_dir.sh` 中的 `STEM` 环境变量。此功能将被直接复用或封装。

4.  **辅助文件管理**：
    *   `~/P4CONFIG`：Perforce 配置文件，定义了 P4CLIENT 和 P4PORT 等环境变量。
    *   `pvtb/env_dir.sh` (或 `env.sh`)：Shell 环境变量设置脚本，定义 `STEM` 环境变量并加载 VCS/Verdi 等 EDA 工具模块。
    *   `sanity_status`, `whether_run_flag`, `configuration_id`, `simulation_sanity_status` (等状态文件)：用于在不同的脚本调用之间传递状态信息，例如构建/仿真是否通过、树是否已运行、当前的 Perforce 变更列表等。

### 3.2 Perforce 客户端管理

`p4client_manage.py` 的功能将集成到新系统中，用于自动化 Perforce 客户端的创建、管理和代码同步，并生成 `P4CONFIG` 文件。系统将智能判断是否需要创建新的客户端或仅更新现有客户端。

### 3.3 PVTB 环境创建与代码转换

`ptb_tree_manage.py`, `ngtb2pvtb_tree_manage.py`, `ngtb2ptb_tree_manage_new.py`, `ngtb2ptb_tree_manage_precise.py` 等脚本将作为可复用组件被统一封装和调用，并根据目标环境类型 (`pvtb_developer` 或 `ppvs`) 进行适配：

*   **环境类型决定脚本调用**：
    *   对于 `pvtb_developer` 环境，系统将主要利用 `ngtb2pvtb_tree_manage.py` 的功能。
    *   对于 `ppvs` 环境，系统将主要利用 `ngtb2ptb_tree_manage_new.py` (或 `ngtb2ptb_tree_manage_precise.py`) 的功能。
*   **目录结构差异化**：系统将能够根据环境类型创建不同的目录结构。
*   **功能精简**：对于 `ppvs` 环境，将明确识别并删除或禁用部分 `pvtb_developer` 环境中的功能，以提供更精简的部署。
*   **Git 仓库管理**：克隆或更新 `pvtb` 仓库。
*   **目录结构创建**：根据 PVTB 环境要求创建必要的目录结构。
*   **Flist 处理**：处理 `from_timescale.compfiles.xf` 文件列表，进行路径转换和文件复制。
*   **RTL 文件转换**：复制、修改（"shell"化）RTL 文件、include 目录，并进行宏定义调整。
*   **环境变量设置**：更新 `pvtb/env_dir.sh` 中的 `STEM` 环境变量，并加载 EDA 工具模块。
*   **配置文件复制**：复制 `configuration_id` 及其他维护文件。
*   **文件内容替换**：执行对 `cp.v` 等文件的内容替换操作。

### 3.4 辅助文件管理

系统将管理和维护 `P4CONFIG`, `pvtb/env_dir.sh`, `sanity_status`, `whether_run_flag`, `configuration_id`, `simulation_sanity_status` 等辅助文件，确保它们在环境搭建过程中正确生成、更新和使用。

## 4. 新功能设计

### 4.1 单命令自动化搭建

新系统将提供两个独立的命令行工具，分别用于搭建不同的 PVTB 环境：

*   **`ppvs_env_setup_developer` (内部开发者环境)**：
    *   **描述**：用于搭建 `pvtb_developer` 环境。
    *   **示例命令**：
    ```bash
    ppvs_env_setup_developer --tree_name my_dev_env --cl 1234567 --debug
    ```
    *   `--tree_name`: 指定要创建或更新的 `pvtb_developer` 环境名称。
    *   `--cl`: (可选) 指定 Perforce changelist 号，用于获取 NGTB RTL 代码。
    *   `--debug`: (可选) 启用详细调试输出。

*   **`ppvs_env_setup_user` (外部用户环境)**：
    *   **描述**：用于搭建 `ppvs` 环境。
    *   **示例命令**：
    ```bash
    ppvs_env_setup_user --tree_name my_user_env --cl 1234567 --debug
    ```
    *   `--tree_name`: 指定要创建或更新的 `ppvs` 环境名称。
    *   `--cl`: (可选) 指定 Perforce changelist 号，用于获取 NGTB RTL 代码。
    *   `--debug`: (可选) 启用详细调试输出。

### 4.2 增强可调试性

为了方便系统维护者进行调试，新系统将提供以下调试特性：

*   **分阶段日志输出**：环境搭建过程将分为多个清晰的阶段（例如：Perforce 同步、NGTB 构建、RTL 转换、PVTB 编译等），每个阶段开始和结束时都会有明确的日志指示。
*   **详细的执行信息**：所有关键操作（如文件复制、内容修改、命令执行）都将输出详细信息，包括源路径、目标路径、修改内容摘要、执行命令及其返回码。
*   **错误捕获与报告**：任何在执行过程中发生的错误都将被捕获，并以清晰、可读的方式报告，包括错误类型、发生位置、相关文件或命令。
*   **临时文件保留**：在调试模式下，可以选择保留所有中间生成的文件和日志，以便事后分析。
*   **状态快照**：在关键节点可以输出当前环境的状态快照（例如，重要的环境变量、文件是否存在、P4 客户端状态等）。

### 4.3 Changelist 指定 RTL 获取

用户可以通过 `--cl` 参数指定一个 Perforce changelist 号。系统将利用 Perforce 的 `p4 sync #<cl_number>` 命令来同步 NGTB RTL 仓库到指定的 CL 状态。这将在 `pvtb_stable_copy_tree_crontab.py` 中 Perforce 同步 NGTB 树的阶段实现。

**实现细节**：

1.  当 `ppvs_env_setup` 接收到 `--cl` 参数时，它会将该 CL 号传递给负责 Perforce 同步的内部模块。

### 4.4 变化文件列表保留

新系统将记录在 PVTB 环境搭建过程中所有被修改、复制或创建的文件。此功能旨在提高可调试性和环境的可追溯性。该列表将包括：

*   **被修改的文件**：记录文件的原始路径和修改后的路径（如果涉及重命名或移动）。
*   **被复制的文件**：记录源文件路径和目标文件路径。
*   **新创建的文件**：记录新创建文件的路径。

**实现细节**：

1.  在环境搭建过程中，Perforce 模块、NGTB 处理模块和 PVTB 转换模块在执行文件操作（修改、复制、创建）时，将同时向日志与报告模块发送文件变更事件。
2.  日志与报告模块将收集这些事件，并生成一个结构化的变化文件列表（例如，JSON 或纯文本格式），存储在特定的日志目录中。
3.  该列表将包含每个变更的详细信息，例如操作类型 (修改/复制/创建)、文件路径、以及可能包含的变更摘要。
4.  在调试模式下，此列表将更加详细，甚至可能包含文件内容的差异 (diff)。

## 5. 高层架构

新系统将采用模块化设计，以提高可维护性和可扩展性。核心组件包括：

*   **主协调器 (`ppvs_env_setup_developer.py` 和 `ppvs_env_setup_user.py`)**：这是用户调用的主脚本，分别负责解析命令行参数、初始化日志系统、协调各个模块的执行顺序，针对各自的环境类型进行特定的流程编排。
*   **配置管理模块**：处理系统配置、环境变量和参数。
*   **Perforce 模块**：封装所有与 Perforce 交互的逻辑，包括客户端管理、同步、CL 获取等，并直接复用 `p4client_manage.py` 的功能。
*   **NGTB 处理模块**：负责 NGTB 环境的同步、构建前修改和构建过程，其功能将直接调用或封装自 `crontab_cmd_pvtb_tree.csh` 和 `pvtb_stable_copy_tree_crontab.py` 等脚本的核心逻辑。
*   **PVTB 转换模块**：负责从 NGTB 到 PVTB 的 RTL 代码转换、文件复制、宏定义和环境变量调整，其功能将直接调用或封装自 `ngtb2pvtb_tree_manage.py`, `ngtb2ptb_tree_manage_new.py`, `ngtb2ptb_tree_manage_precise.py`, `ptb_tree_manage.py` 等脚本的核心逻辑，并根据环境类型（`pvtb_developer` 或 `ppvs`）执行差异化处理。
*   **日志与报告模块**：统一处理所有日志输出、错误报告和状态快照。

```mermaid
graph TD
    A1["ppvs_env_setup_developer.py (Main Coordinator for Developer Env)"] --> B(配置管理模块)
    A1 --> C(Perforce 模块)
    A1 --> D(NGTB 处理模块)
    A1 --> E(PVTB 转换模块)
    A1 --> F(日志与报告模块)

    A2["ppvs_env_setup_user.py (Main Coordinator for User Env)"] --> B
    A2 --> C
    A2 --> D
    A2 --> E
    A2 --> F

    C --> G_p4client[p4client_manage.py (Internal)]
    D --> H_pvtb_stable[pvtb_stable_copy_tree_crontab.py (Internal)]
    E --> I_ngtb2pvtb[ngtb2pvtb_tree_manage.py (Internal)]
    E --> J_ngtb2ptb[ngtb2ptb_tree_manage_new.py / ngtb2ptb_tree_manage_precise.py (Internal)]

    subgraph Existing Scripts (Encapsulated)
        G_p4client
        H_pvtb_stable
        I_ngtb2pvtb
        J_ngtb2ptb
        K_ptb_tree[ptb_tree_manage.py (Internal)]

        H_pvtb_stable --> I_ngtb2pvtb
        H_pvtb_stable --> J_ngtb2ptb
        I_ngtb2pvtb --> K_ptb_tree
        J_ngtb2ptb --> K_ptb_tree
    end
```

## 6. 执行流程 (新系统)

以下是使用新系统命令搭建环境的典型执行流程，分为 `pvtb_developer` 和 `ppvs` 两种环境：

### 6.1 `ppvs_env_setup_developer` (内部开发者环境) 执行流程

1.  **命令行解析**：`ppvs_env_setup_developer.py` 解析用户提供的参数，如 `tree_name`, `cl`, `debug`。
2.  **日志系统初始化**：根据 `debug` 参数设置日志级别和输出目标。
3.  **Perforce 客户端检查与设置**：
    *   调用 Perforce 模块检查或创建 P4 客户端，其中会复用 `p4client_manage.py` 的功能。
    *   生成或更新 `P4CONFIG` 文件。
4.  **NGTB 环境准备**：
    *   调用 Perforce 模块，根据是否指定 `--cl` 参数，同步 NGTB RTL 树到最新版本或指定 CL 号。
    *   调用 NGTB 处理模块（包含 `Makefile`, `sh_itrace.cpp` 等文件修改及 `hbo` 构建的直接调用或封装逻辑）。
5.  **PVTB 树目录与 Git 仓库管理**：
    *   调用 PVTB 转换模块，创建目标 `pvtb_developer` 树目录。
    *   克隆或更新 `pvtb` Git 仓库（直接调用或封装逻辑）。
6.  **RTL 代码转换与复制**：
    *   调用 PVTB 转换模块 (集成 `ngtb2pvtb_tree_manage.py` 的直接调用或封装核心逻辑)，处理 `from_timescale.compfiles.xf`，复制和转换 RTL 文件及 include 目录。
    *   对核心 RTL 文件进行 "shell" 化修改和宏定义调整（直接调用或封装逻辑）。
7.  **环境变量与配置文件更新**：
    *   调用 PVTB 转换模块，更新 `pvtb/env_dir.sh` 中的 `STEM` 环境变量（直接调用或封装逻辑）。
    *   复制 `configuration_id` 和其他辅助状态文件（直接调用或封装逻辑）。
8.  **PVTB 编译**：
    *   **注意**：根据 `flow_filelist.md` 的说明，PVTB 编译 (`run_ptb.py` 负责) 不包含在树搭建流程中。新系统将仅搭建环境，编译过程仍需用户在环境搭建完成后独立触发。
9.  **结果报告**：系统输出环境搭建成功或失败的摘要，并指示如何查看详细日志进行调试。

### 6.2 `ppvs_env_setup_user` (外部用户环境) 执行流程

1.  **命令行解析**：`ppvs_env_setup_user.py` 解析用户提供的参数，如 `tree_name`, `cl`, `debug`。
2.  **日志系统初始化**：根据 `debug` 参数设置日志级别和输出目标。
3.  **Perforce 客户端检查与设置**：
    *   调用 Perforce 模块检查或创建 P4 客户端，其中会复用 `p4client_manage.py` 的功能。
    *   生成或更新 `P4CONFIG` 文件。
4.  **NGTB 环境准备**：
    *   调用 Perforce 模块，根据是否指定 `--cl` 参数，同步 NGTB RTL 树到最新版本或指定 CL 号。
    *   调用 NGTB 处理模块（包含 `Makefile`, `sh_itrace.cpp` 等文件修改及 `hbo` 构建的直接调用或封装逻辑）。
5.  **PVTB 树目录与 Git 仓库管理**：
    *   调用 PVTB 转换模块，创建目标 `ppvs` 树目录，该目录结构将与 `pvtb_developer` 环境有所差异。
    *   克隆或更新 `pvtb` Git 仓库（直接调用或封装逻辑）。
6.  **RTL 代码转换与复制**：
    *   调用 PVTB 转换模块 (集成 `ngtb2ptb_tree_manage_new.py`/`ngtb2ptb_tree_manage_precise.py` 的直接调用或封装核心逻辑)，处理 `from_timescale.compfiles.xf`，复制和转换 RTL 文件及 include 目录。
    *   对核心 RTL 文件进行 "shell" 化修改和宏定义调整（直接调用或封装逻辑）。
    *   **功能精简**：在此阶段，根据 `ppvs` 环境的要求，删除或禁用部分 `pvtb_developer` 环境中的功能（直接调用或封装逻辑）。
7.  **环境变量与配置文件更新**：
    *   调用 PVTB 转换模块，更新 `pvtb/env_dir.sh` 中的 `STEM` 环境变量（直接调用或封装逻辑）。
    *   复制 `configuration_id` 和其他辅助状态文件（直接调用或封装逻辑）。
8.  **PVTB 编译**：
    *   **注意**：与 `pvtb_developer` 环境相同，PVTB 编译不包含在树搭建流程中。
9.  **结果报告**：系统输出环境搭建成功或失败的摘要，并指示如何查看详细日志进行调试。

## 7. 未来考虑

*   **配置文件支持**：允许通过配置文件（例如 YAML 或 JSON）指定更复杂的搭建参数和默认值。
*   **并行化优化**：对于一些独立的操作，可以考虑引入并行执行以缩短搭建时间。
*   **GUI 接口**：长期目标可以考虑提供一个图形用户界面，进一步简化用户操作。
*   **版本管理**：集成对不同 PVTB 环境配置的版本管理功能。
