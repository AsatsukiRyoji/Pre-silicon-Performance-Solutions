# PVTB 树搭建流程中与 `ngtb2ptb_tree_manage_new.py` 支线相关的脚本和文件列表

本文档总结了 PVTB (Pre-Silicon Verification Test Bench) 环境搭建过程中，特别是与 `ngtb2ptb_tree_manage_new.py` 支线相关的核心脚本和文件，包括相关的 crontab 自动化流程，但不包含 PVTB 验证（编译、测试生成和仿真）阶段。

## 1. Crontab 定时任务入口及相关脚本

这些脚本是 crontab 定时任务的入口点，用于自动化执行 PVTB 环境的维护和更新，特别是针对 `ngtb2ptb_tree_manage_new.py` 所涉及的树类型。

*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/crontab_cmd_pvtb_tree.csh`
    *   **描述**: C-shell 驱动脚本，用于管理 `tree1forcp_pvtb_sanity_tree` 和 `tree2forcp_pvtb_sanity_tree`。它根据 `simulation_sanity_status` 和 `whether_run_flag` 文件决定执行哪个树，并调用 `pvtb_stable_copy_tree_crontab.py`。
*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/pvtb_stable_copy_tree_crontab.py`
    *   **描述**: Python 逻辑脚本，由 `crontab_cmd_pvtb_tree.csh` 调用。负责 NGTB (GC) 树的 Perforce 同步、修改特定的 `Makefile` 和 `sh_itrace.cpp` 文件、运行 `hbo` 构建命令。如果 NGTB 构建通过，它会调用 `ngtb2pvtb_tree_manage.py` 或其变种（例如 `ngtb2ptb_tree_manage_new.py`）复制 NGTB 树到 PVTB 目标树，并进行 PVTB 的编译。
*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/eda_modulefile`
    *   **描述**: EDA (Electronic Design Automation) 工具链模块文件，用于在 C-shell 脚本中卸载和加载特定版本的 VCS 和 Verdi 工具，确保环境一致性。

## 2. Perforce 客户端管理

*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/p4client_manage.py`
    *   **描述**: 用于创建和管理 Perforce 客户端工作空间。它根据用户输入生成客户端规范，执行 `p4 client -i` 命令创建客户端，然后执行 `p4 sync` 同步代码，并生成 `P4CONFIG` 文件。这是所有基于 Perforce 的环境设置的基础。

## 3. PVTB 环境创建与代码转换

这些脚本负责从 NGTB 环境中提取、转换和配置 RTL 代码，以构建 PVTB 环境。`ngtb2ptb_tree_manage_new.py` 是此过程中的一个核心执行者，通常由 `pvtb_stable_copy_tree_crontab.py` 等脚本调用。

*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/ptb_tree_manage.py`
    *   **描述**: 主要用于管理 PVTB 树的 Python 脚本。它处理 Git 仓库（克隆/更新 `pvtb` 仓库）、复制静态源文件、修改 `pvtb/env_dir.sh` 文件中的 `STEM` 环境变量、处理 `from_timescale.compfiles.xf` 文件列表（路径转换）、进行文件内容替换（例如针对 `cp.v`），并复制 `configuration_id` 和维护文件。它还支持通过 Perforce `changelist` 或 `shelve` 同步代码。
*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/ngtb2pvtb_tree_manage.py`
    *   **描述**: Python 脚本，用于从 NGTB 环境创建 PVTB 环境。其功能与 `ngtb2ptb_tree_manage_new.py` 高度相似，可能作为其通用版本或被其内部调用。负责 Git 仓库管理、目录结构创建、Flist 处理、路径转换与文件复制、Shell 模块替换与修改、宏定义修改、C-shell 文件修改以及配置文件复制。
*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/ngtb2ptb_tree_manage_new.py`
    *   **描述**: 本次关注的核心 Python 脚本，用于从 NGTB 环境创建 PVTB 环境。具体功能包括 Git 仓库管理、目录结构创建、Flist 处理、路径转换与文件复制、Shell 模块替换与修改、宏定义修改、C-shell 文件修改以及配置文件复制。
*   `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/ngtb2ptb_tree_manage_precise.py`
    *   **描述**: 类似于 `ngtb2ptb_tree_manage_new.py`，可能是其另一个变种，提供更精确或略有不同的文件处理和转换逻辑，用于特定的 PVTB 树搭建场景。

## 4. 辅助文件

*   `~/P4CONFIG`
    *   **描述**: Perforce 配置文件，定义了 P4CLIENT 和 P4PORT 等环境变量，用于 Perforce 命令的正确执行。由 `p4client_manage.py` 生成。
*   `pvtb/env_dir.sh` (或 `env.sh`)
    *   **描述**: Shell 环境变量设置脚本。定义了 `STEM` 环境变量，指向 PVTB 树的根目录，并加载 VCS/Verdi 等 EDA 工具模块。由 `ptb_tree_manage.py` 或 `ngtb2ptb_tree_manage_new.py` 进行修改。
*   `sanity_status`, `whether_run_flag`, `configuration_id`, `simulation_sanity_status` (等状态文件)
    *   **描述**: 这些是 PVTB 树根目录下或日志目录中的文本文件，用于在不同的脚本调用之间传递状态信息，例如构建/仿真是否通过、树是否已运行、当前的 Perforce 变更列表等。在 crontab 流程中扮演关键角色，用于实现故障转移和交替运行逻辑。

## 5. 脚本执行顺序概述 (与 `ngtb2ptb_tree_manage_new.py` 支线相关)

PVTB 环境的搭建和更新流程通常由 `crontab` 定时任务触发，并涉及多个脚本的协同工作。以下是与 `ngtb2ptb_tree_manage_new.py` 支线相关的核心脚本的执行顺序概述：

1.  **Crontab 定时任务触发**:
    *   **入口点**: 定时任务会执行 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/crontab_cmd_pvtb_tree.csh`。
    *   **环境初始化**: `crontab_cmd_pvtb_tree.csh` 会首先 `source ~/.cshrc` 和 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/eda_modulefile` 来设置 shell 和 EDA 工具环境。
    *   **状态检查与决策**: `crontab_cmd_pvtb_tree.csh` 会读取 `simulation_sanity_status` 和 `whether_run_flag` 等状态文件，根据这些信息决定接下来要运行哪个 PVTB 树（例如，故障转移或交替执行）。

2.  **Perforce 客户端管理 (如果尚未设置或需要更新)**:
    *   **手动/一次性执行**: `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/p4client_manage.py` 通常在首次设置新的 PVTB 工作空间时手动执行，用于创建 Perforce 客户端、同步初始代码并生成 `P4CONFIG` 文件。在自动化流程中，通常假设客户端已存在并配置好。

3.  **PVTB 环境搭建与代码转换**:
    *   **主要执行者**: `crontab_cmd_pvtb_tree.csh` 会根据决策调用 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/crontab/crontab_pvtb/pvtb_stable_copy_tree_crontab.py`。
    *   **内部调用**: `pvtb_stable_copy_tree_crontab.py` 会负责 NGTB (GC) 树的 Perforce 同步，并进一步调用 `/home/jiangxiaofei/Pre-silicon-Performance-Solutions/pvtb/script/ngtb2pvtb_tree_manage.py` 或其变种（如 `ngtb2ptb_tree_manage_new.py`/`ngtb2ptb_tree_manage_precise.py`）来完成核心搭建工作，包括：
        *   Git 仓库的克隆/更新。
        *   目标 PVTB 目录结构的创建。
        *   从 NGTB 编译文件列表 (`from_timescale.compfiles.xf`) 中复制和转换 RTL 文件、include 目录。
        *   对核心 RTL 文件进行“shell”化修改和宏定义调整。
        *   复制 `configuration_id` 和其他维护文件。
        *   更新 `pvtb/env_dir.sh` 中的 `STEM` 环境变量。

**注意事项**：

*   `run_ptb.py` 脚本负责 PVTB 环境中的编译、测试生成和仿真，但这些环节不包含在本总结中，它们是在 PVTB 树搭建完成后，在已配置的环境中独立执行的验证流程。
*   上述步骤是与 `ngtb2ptb_tree_manage_new.py` 支线相关的典型执行顺序。具体的调用关系和逻辑可能因 `crontab` 任务的配置和 PVTB 树的类型而略有不同。
