#!/usr/bin/env python3
"""
@Describe: This script duplicates and modifies RTL files to support 2-core instantiation.
@Author: Zheng Yu
Data: 2025.09.26
RTL 2xcd Support Script
"""

import os
import re
import shutil
import sys
import glob

# ========================
# Global Configuration
# ========================
# Get STEM path from environment variable
STEM = os.environ['STEM']
DEBUG = True  # Enable detailed debug output
MODIFICATION_FLAG = "//Modified by 1xcd_rtl_trans_2xcd script"
def debug_print(msg):
    """Print debug messages if DEBUG is enabled"""
    if DEBUG:
        print(f"[DEBUG] {msg}")

def error_exit(file_path, message, line_num=None, line_content=None):
    """Report error with file location and exit"""
    print(f"\n[ERROR] {file_path}")
    if line_num and line_content:
        print(f"Line {line_num}: {line_content.strip()}")
    print(f"Error: {message}")
    sys.exit(1)

# ========================
# Path Handling Functions
# ========================
def create_directory(path):
    """Create directory if it doesn't exist"""
    debug_print(f"Creating directory: {path}")
    os.makedirs(path, exist_ok=True)
    return path

def copy_file(src, dst):
    """Copy file with debug logging"""
    debug_print(f"Copying {src} to {dst}")
    shutil.copy2(src, dst)
    return dst

def resolve_path(path):
    """Resolve paths containing $STEM"""
    if '$STEM' in path:
        resolved = path.replace('$STEM', STEM)
        debug_print(f"Resolved path: {path} -> {resolved}")
        return resolved
    return os.path.join(STEM, path)

def find_file_in_rtlf(filename):
    """Find file path in rtl.f with exact filename matching"""
    rtl_f_path = os.path.join(STEM, 'pvtb', 'rtl.f')
    debug_print(f"Searching for '{filename}' in {rtl_f_path}")
    
    with open(rtl_f_path) as f:
        for line_num, line in enumerate(f, 1):
            clean_line = line.strip().replace('-v','').strip()
            if clean_line.endswith(filename):
                full_path = resolve_path(clean_line)
                
                # Check if file exists
                if os.path.exists(full_path):
                    debug_print(f"Found at line {line_num}: {line} -> {full_path}")
                    return full_path
                
                # Try glob pattern matching
                matches = glob.glob(full_path)
                if matches:
                    debug_print(f"Found via glob: {matches[0]}")
                    return matches[0]
                
                error_exit(rtl_f_path, f"Path found but file not exist: {full_path}", line_num, line)
    
    error_exit(rtl_f_path, f"No entry matching '*{filename}' found")

# ========================
# File Processing Functions
# ========================
def modify_block_hierarchy_vh(file_path):
    debug_print(f"Modifying original file: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if MODIFICATION_FLAG in content:
        debug_print("File already modified, skipping")
        return file_path
    
    lines = content.split('\n')
    new_lines = [MODIFICATION_FLAG]

    if not any('`ifndef PVTB_2DIE_RTL' in line for line in lines):
        new_lines.append('`ifndef PVTB_2DIE_RTL')
        debug_print("Added `ifndef PVTB_2DIE_RTL at beginning")
    
    for i, line in enumerate(lines):
        if re.search(r'`ifndef\s+__BLOCK_HIERARCHY__', line):
            new_lines.append('// ' + line)
            debug_print(f"Commented out `ifndef __BLOCK_HIERARCHY__ at line {i+1}")
        elif re.search(r'`define\s+__BLOCK_HIERARCHY__', line):
            new_lines.append('// ' + line)
            debug_print(f"Commented out `define __BLOCK_HIERARCHY__ at line {i+1}")
        elif '`endif' in line and '__BLOCK_HIERARCHY__' not in line:
            new_lines.append('// ' + line)
            debug_print(f"Commented out `endif at line {i+1}")
        else:
            new_lines.append(line)
    
    original_content = '\n'.join(new_lines)
    
    new_content = original_content + '\n`else\n'
    debug_print("Added `else after original content")
    
    core0_content = original_content
    lines_to_remove =['`ifndef PVTB_2DIE_RTL',
                      '`ifndef __BLOCK_HIERARCHY__',
                      '`ifdef __BLOCK_HIERARCHY__']
    core0_lines = []
    for line in core0_content.split('\n'):
        stripped_line = line.strip()
        if stripped_line not in lines_to_remove and not stripped_line.startswith('//'+lines_to_remove[0]):
            core0_lines.append(line)
    core0_content ='\n'.join(core0_lines)

    core0_content = core0_content.replace('core', 'core0')
    new_content += core0_content
    debug_print("Added core0 version with replacements")
    core1_content = original_content
    lines_to_remove =['`ifndef PVTB_2DIE_RTL',
                      '`ifndef __BLOCK_HIERARCHY__',
                      '`ifdef __BLOCK_HIERARCHY__']
    core1_lines = []
    for line in core1_content.split('\n'):
        stripped_line = line.strip()
        if stripped_line not in lines_to_remove and not stripped_line.startswith('//'+lines_to_remove[0]):
            core1_lines.append(line)
    core1_content ='\n'.join(core1_lines)

    core1_content = core1_content.replace('core', 'core1')
    core1_content = core1_content.replace('        ', '__1     ')
    core1_content = core1_content.replace('CTNR   ', 'CTNR__1   ')
    new_content += core1_content
    debug_print("Added core1 version with replacements")
    
    new_content += '\n`endif\n'
    debug_print("Added final `endif")
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    return file_path

def create_block_hierarchy_1_vh(src_path, dst_path):
    debug_print(f"Creating modified file: {dst_path} from {src_path}")

    if os.path.exists(dst_path):
        with open(dst_path,'r')as f:
            content =f.read()
            if MODIFICATION_FLAG in content:
                debug_print("File already modified, skipping")
                return dst_path

    shutil.copy2(src_path, dst_path)
    debug_print("Copied original file to new location")
    
    with open(dst_path, 'r') as f:
        content = f.read()
    new_content = MODIFICATION_FLAG+'\n'+content
    
    lines = new_content.split('\n')
    new_lines = []
    
    if not any('`ifndef PVTB_2DIE_RTL' in line for line in lines):
        new_lines.append('`ifdef PVTB_2DIE_RTL')
        debug_print("Added `ifndef PVTB_2DIE_RTL at beginning")
    
    for i, line in enumerate(lines):
        if re.search(r'`ifndef\s+__BLOCK_HIERARCHY__', line):
            new_lines.append('// ' + line)
            debug_print(f"Commented out `ifndef __BLOCK_HIERARCHY__ at line {i+1}")
        elif re.search(r'`define\s+__BLOCK_HIERARCHY__', line):
            new_lines.append('// ' + line)
            debug_print(f"Commented out `define __BLOCK_HIERARCHY__ at line {i+1}")
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    content = content.replace('core', 'core1')
    debug_print("Replaced all 'core' with 'core1'")
    
    with open(dst_path, 'w') as f:
        f.write(content)
    
    return dst_path

def process_core_v(rtl_2xcd_path):
    """Process core.v -> core1.v"""
    # Find source file
    src_path = find_file_in_rtlf("src/rtl/core.v")
    dst_path = os.path.join(rtl_2xcd_path, 'core1.v')
    debug_print(f"Processing {src_path} -> {dst_path}")
    
    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Comment out include lines
    for i, line in enumerate(lines):
        if '`include' in line:
            lines[i] = f"// {line}"
            debug_print(f"Commented include at line {i+1}")
    
    # 2. Change module name
    module_found = False
    for i, line in enumerate(lines):
        if 'module core' in line:
            if module_found:
                error_exit(src_path, "Multiple 'module core' declarations found", i+1, line)
            lines[i] = line.replace('module core', 'module core1')
            module_found = True
            debug_print(f"Modified module declaration at line {i+1}")
    
    if not module_found:
        error_exit(src_path, "'module core' declaration not found")
    
    # 3-4. Change instance names
    replacements = [
        ('core_monitors monitors', 'core_monitors__1 monitors'),
        ('sq_monitors sq_monitors', 'sq_monitors__1 sq_monitors')
    ]
    
    for old, new in replacements:
        found = False
        for i, line in enumerate(lines):
            if old in line:
                lines[i] = line.replace(old, new)
                found = True
                debug_print(f"Replaced '{old}' with '{new}' at line {i+1}")
        if not found:
            error_exit(src_path, f"Pattern '{old}' not found")
    
    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return dst_path

def process_core_monitors(rtl_2xcd_path):
    """Process core_monitors.v -> core_monitors__1.v"""
    src_path = find_file_in_rtlf("core_monitors.v")
    dst_path = os.path.join(rtl_2xcd_path, 'core_monitors__1.v')
    debug_print(f"Processing {src_path} -> {dst_path}")
    
    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Change include
    for i, line in enumerate(lines):
        if 'block_hierarchy.vh' in line:
            lines[i] = line.replace('block_hierarchy.vh', 'block_hierarchy__1.vh')
            debug_print(f"Modified include at line {i+1}")
    
    # 2. Change module name
    module_found = False
    for i, line in enumerate(lines):
        if 'module core_monitors' in line:
            lines[i] = line.replace('module core_monitors', 'module core_monitors__1')
            module_found = True
            debug_print(f"Modified module declaration at line {i+1}")
    
    if not module_found:
        error_exit(src_path, "'module core_monitors' declaration not found")
    
    # 3-4. Change instance names
    patterns = [
        (r'\.instance_name\("', '.instance_name("core1__'),
        (r'\.instance_lcname\("', '.instance_lcname("core1__')
    ]
    
    for pattern, replacement in patterns:
        found = False
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                lines[i] = re.sub(pattern, replacement, line)
                found = True
                debug_print(f"Modified instance at line {i+1}")
        if not found:
            error_exit(src_path, f"Pattern '{pattern}' not found")
    
    # 5. Add original include
    lines.append('\n`include "block_hierarchy.vh"')
    debug_print("Added original include at end")
    
    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return dst_path

def process_monitor_spi_sq_trace(rtl_2xcd_path):
    """Process monitor_spi_sq_trace.sv -> monitor_spi_sq_trace__1.sv"""
    src_path = find_file_in_rtlf("monitor_spi_sq_trace.sv")
    dst_path = os.path.join(rtl_2xcd_path, 'monitor_spi_sq_trace__1.sv')
    debug_print(f"Processing {src_path} -> {dst_path}")
    
    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Change module name
    modified = False
    for i, line in enumerate(lines):
        if 'module monitor_spi_sq_trace' in line:
            lines[i] = line.replace('module monitor_spi_sq_trace', 'module monitor_spi_sq_trace__1')
            modified = True
            debug_print(f"Modified module name at line {i+1}")
    
    if not modified:
        error_exit(src_path, "'module monitor_spi_sq_trace' declaration not found")
    
    # 2. Change strap ID range
    modified = False
    for i, line in enumerate(lines):
        if '`CORE_STRAP_ID_RANGE' in line:
            lines[i] = line.replace('`CORE_STRAP_ID_RANGE', '2:0')
            modified = True
            debug_print(f"Modified strap ID range at line {i+1}")
    
    if not modified:
        debug_print("ERROR: Strap ID range not modified - pattern not found")
    
    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return dst_path

def process_monitor_sq_inst_trace(rtl_2xcd_path):
    """Process monitor_sq_inst_trace.sv -> monitor_sq_inst_trace__1.sv"""
    src_path = find_file_in_rtlf("monitor_sq_inst_trace.sv")
    dst_path = os.path.join(rtl_2xcd_path, 'monitor_sq_inst_trace__1.sv')
    debug_print(f"Processing {src_path} -> {dst_path}")
    
    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Change module name
    modified = False
    for i, line in enumerate(lines):
        if 'module monitor_sq_inst_trace' in line:
            lines[i] = line.replace('module monitor_sq_inst_trace', 'module monitor_sq_inst_trace__1')
            modified = True
            debug_print(f"Modified module name at line {i+1}")
    
    if not modified:
        error_exit(src_path, "'module monitor_sq_inst_trace' declaration not found")
    
    # 2. Change strap ID range
    modified = False
    for i, line in enumerate(lines):
        if '`CORE_STRAP_ID_RANGE' in line:
            lines[i] = line.replace('`CORE_STRAP_ID_RANGE', '2:0')
            modified = True
            debug_print(f"Modified strap ID range at line {i+1}")
    
    if not modified:
        debug_print("ERROR: Strap ID range not modified - pattern not found")
    
    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return dst_path

def process_sq_monitor(rtl_2xcd_path):
    """Process sq_monitors.sv -> sq_monitors__1.sv"""
    src_path = find_file_in_rtlf("sq_monitors.sv")
    dst_path = os.path.join(rtl_2xcd_path, 'sq_monitors__1.sv')
    debug_print(f"Processing {src_path} -> {dst_path}")
    
    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Change include
    for i, line in enumerate(lines):
        if 'block_hierarchy.vh' in line:
            lines[i] = line.replace('block_hierarchy.vh', 'block_hierarchy__1.vh')
            debug_print(f"Modified include at line {i+1}")
    
    # 2. Change module name
    module_found = False
    for i, line in enumerate(lines):
        if 'module sq_monitors' in line:
            lines[i] = line.replace('module sq_monitors', 'module sq_monitors__1')
            module_found = True
            debug_print(f"Modified module declaration at line {i+1}")
    
    if not module_found:
        error_exit(src_path, "'module sq_monitors' declaration not found")
    
    # 3. Change instance names
    pattern = r'sq_monitors_se(\d+)_sh(\d+)_cu(\d+) se(\d+)_sh(\d+)_cu(\d+)_monitors'
    replacement = r'sq_monitors_se\1_sh\2_cu\3__1 se\4_sh\5_cu\6_monitors'
    
    found = False
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            lines[i] = re.sub(pattern, replacement, line)
            found = True
            debug_print(f"Modified instance name at line {i+1}")
    
    if not found:
        error_exit(src_path, f"Pattern '{pattern}' not found")
    
    # 4. Modify for loop
    for i, line in enumerate(lines):
        if 'for(se_id = 0; se_id < `GPU__GC__NUM_SE' in line:
            lines[i] = lines[i].replace('se_id = 0', "se_id = 0+'d4")
            lines[i] = lines[i].replace('NUM_SE', "NUM_SE+'d4")
            debug_print(f"Modified for loop at line {i+1}")
            break
    else:
        error_exit(src_path, "For loop pattern not found")
    
    # 5. Add original include
    lines.append('\n`include "block_hierarchy.vh"')
    debug_print("Added original include at end")
    
    # 6. Comment out itrace_delete_dpi
    for i, line in enumerate(lines):
        if 'itrace_delete_dpi();' in line:
            lines[i] = f"// {line}"
            debug_print(f"Commented itrace_delete_dpi at line {i+1}")
            break
    else:
        debug_print("Warning: itrace_delete_dpi not found")
    
    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return dst_path

def process_sq_monitor_se_sh_cu(rtl_2xcd_path):
    """Process sq_monitors_se_sh_cu.sv -> sq_monitors_se_sh_cu__1.sv"""
    src_path = find_file_in_rtlf("sq_monitors_se_sh_cu.sv")
    dst_path = os.path.join(rtl_2xcd_path, 'sq_monitors_se_sh_cu__1.sv')
    debug_print(f"Processing {src_path} -> {dst_path}")
    
    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Change include
    for i, line in enumerate(lines):
        if 'block_hierarchy.vh' in line:
            lines[i] = line.replace('block_hierarchy.vh', 'block_hierarchy__1.vh')
            debug_print(f"Modified include at line {i+1}")
    
    # 2. Change module name
    pattern = r'module\s+sq_monitors_se(\d+)_sh(\d+)_cu(\d+)'
    replacement = r'module sq_monitors_se\1_sh\2_cu\3__1'
    
    found = False
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            lines[i] = re.sub(pattern, replacement, line)
            found = True
            debug_print(f"Modified module name at line {i+1}")
    
    if not found:
        error_exit(src_path, f"Module pattern '{pattern}' not found")
    
    # 3. Modify SE_id_strap_id
    pattern = r'SE_id_strap_id),'
    replacement = r"SE_id_strap_id+'d4),"
    
    found = False
    for i, line in enumerate(lines):
        if pattern in line:
            lines[i] = line.replace(pattern, replacement)
            found = True
            debug_print(f"Modified SE_id_strap_id at line {i+1}")
    
    if not found:
        error_exit(src_path, f"Pattern '{pattern}' not found")

    pattern = r'monitor_spi_sq_trace'
    replacement = r'monitor_spi_sq_trace__1'
    found = False
    for i, line in enumerate(lines):
        if pattern in line:
            lines[i] = line.replace(pattern, replacement)
            found = True
            debug_print(f"Modified monitor_spi_sq_trace__1 inst at line {i+1}")

    if not found:
        error_exit(src_path, f"Pattern '{pattern}' not found")

    pattern = r'monitor_sq_inst_trace'
    replacement = r'monitor_sq_inst_trace__1'
    found = False
    for i, line in enumerate(lines):
        if pattern in line:
            lines[i] = line.replace(pattern, replacement)
            found = True
            debug_print(f"Modified monitor_sq_inst_trace__1 inst at line {i+1}")

    if not found:
        error_exit(src_path, f"Pattern '{pattern}' not found")

    for i in range(4):
        pattern = f'set_vgpr_size_dpi({i},'
        replacement = f'set_vgpr_size_dpi({i+4},'
        found = False
        for i, line in enumerate(lines):
            if pattern in line:
                lines[i] = line.replace(pattern, replacement)
                found = True
                debug_print(f"Modified  inst at line {i+1}")
        if not found:
            error_exit(src_path, f"Pattern '{pattern}' not found")
    for i in range(4):
        pattern = f'itrace_td_sq_rddone_monitor_dpi({i},'
        replacement = f'itrace_td_sq_rddone_monitor_dpi({i+4},'
        found = False
        for i, line in enumerate(lines):
            if pattern in line:
                lines[i] = line.replace(pattern, replacement)
                found = True
                debug_print(f"Modified  inst at line {i+1}")
        if not found:
            error_exit(src_path, f"Pattern '{pattern}' not found")
    for i in range(4):
        pattern = f'itrace_td_sp_data_monitor_dpi({i},'
        replacement = f'itrace_td_sp_data_monitor_dpi({i+4},'
        found = False
        for i, line in enumerate(lines):
            if pattern in line:
                lines[i] = line.replace(pattern, replacement)
                found = True
                debug_print(f"Modified  inst at line {i+1}")
        if not found:
            error_exit(src_path, f"Pattern '{pattern}' not found")
    for i in range(4):
        pattern = f'{i}, 0,'
        replacement = f'{i+4}, 0,'
        found = False
        for i, line in enumerate(lines):
            if pattern in line:
                lines[i] = line.replace(pattern, replacement)
                found = True
                debug_print(f"Modified  inst at line {i+1}")
        if not found:
            error_exit(src_path, f"Pattern '{pattern}' not found")
        #itrace_vdata_monitor_dpi(dbg_id,
        #                                 0, 0,
        #itrace_vdata_monitor_dpi(dbg_id,
        #                                 4, 0,

    # 4. Add original include
    lines.append('\n`include "block_hierarchy.vh"')
    debug_print("Added original include at end")
    
    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return dst_path

def process_monitor_sp_rtl_trace(rtl_2xcd_path):
    src_path = os.path.join(STEM,'src','rtl','monitor_sp_rtl_trace.sv')

    if not os.path.exists(src_path):
        error_exit(src_path,"File not found")

    dst_path = os.path.join(STEM,'src','rtl','monitor_sp_rtl_trace.sv')
    debug_print(f"Processing {src_path} ->{dst_path}")

    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')
        
    modified =False
    for i,line in enumerate (lines):
        if '`CORE_STRAP_ID_RANGE' in line:
            lines[i] = line.replace('`CORE_STRAP_ID_RANGE', '2:0')
            modified = True
            debug_print(f"Modified strap ID range at line {i+1}")
    
    if not modified:
        debug_print("wraning: Strap ID range not modified - pattern not found")

    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    return dst_path

def process_sp_itrace_monitor_instance(rtl_2xcd_path):
    src_path = os.path.join(STEM,'src','vega20c','library','gc-vega20c','pub','src','rtl','sp_itrace_monitor_instance.v')

    if not os.path.exists(src_path):
        error_exit(src_path,"File not found")

    dst_path = os.path.join(STEM,'src','vega20c','library','gc-vega20c','pub','src','rtl','sp_itrace_monitor_instance.v')
    debug_print(f"Processing {src_path} ->{dst_path}")

    with open(src_path) as f:
        content = f.read()
        lines = content.split('\n')

    if MODIFICATION_FLAG in content:
        debug_print("File already modified, skipping")
        return dst_path
    
    lines  += [MODIFICATION_FLAG]
    modified =False
    for i,line in enumerate (lines):
        if '.se_id(se_id)' in line:
            lines[i] = line.replace('.se_id(se_id),', "`ifndef PVTB_2DIE_RTL \n  .se_id(se_id),\n  `else \n  .se_id(  ),\n  `endif")
            modified = True
            debug_print(f"Modified strap ID range at line {i+1}")
    
    if not modified:
        debug_print("wraning: Strap ID range not modified - pattern not found")

    with open(dst_path, 'w') as f:
        f.write('\n'.join(lines))
    return dst_path

# ========================
# rtl_2xcd.f Update Function
# ========================
def update_rtl_2xcd_f(rtl_2xcd_path, new_files):
    """Update rtl_2xcd.f file with new paths"""
    dst_f = os.path.join(STEM, 'pvtb', 'rtl_2xcd.f')
    debug_print(f"Updating {dst_f}")

    # 1. Replace paths for modified files
    modified_files = [
        ('src/rtl/core.v', 'core1.v'),
        ('core_monitors.v', 'core_monitors__1.v'),
        ('monitor_spi_sq_trace.sv', 'monitor_spi_sq_trace__1.sv'),
        ('monitor_sq_inst_trace.sv', 'monitor_sq_inst_trace__1.sv'),
        ('sq_monitors.sv', 'sq_monitors__1.sv'),
        ('sq_monitors_se_sh_cu.sv', 'sq_monitors_se_sh_cu__1.sv')
    ]
    
    with open(dst_f, 'r') as f:
        content = f.read()
        
    # 2. Add new files section
    content += "\n\n// Added files for core1\n"
    content += f"+incdir+$STEM/src/rtl_2xcd/\n"
    for file in new_files:
        rel_path = os.path.relpath(file,STEM)
        content += f"$STEM/{rel_path}\n"
        debug_print(f"Added new file: $STEM/{rel_path}")
    
    with open(dst_f, 'w') as f:
        f.write(content)
    


# ========================
# Main Workflow
# ========================
def main():
    print(f"\nStarting core duplication with STEM={STEM}")
    
    try:
        # 1. Create target directory
        rtl_2xcd_path = create_directory(os.path.join(STEM, 'src', 'rtl', 'rtl_2xcd'))
        
        # 2. Copy rtl.f to rtl_2xcd.f
        src_rtl_f = os.path.join(STEM,'pvtb', 'rtl.f')
        dst_rtl_f = os.path.join(STEM,'pvtb', 'rtl_2xcd.f')
        copy_file(src_rtl_f, dst_rtl_f)

        src_bh_path = os.path.join(STEM, 'src','vega20c','common','pub','src','rtl','bia_ifrit_logical' , 'block_hierarchy.vh')
        dst_bh1_path = os.path.join(STEM, 'src','vega20c','common','pub','src','rtl','bia_ifrit_logical' , 'block_hierarchy__1.vh')

        create_block_hierarchy_1_vh(src_bh_path, dst_bh1_path)

        modify_block_hierarchy_vh(src_bh_path)#modify

        # 3. Process all files
        new_files = []
        
        
        # Core files
        core_file = process_core_v(rtl_2xcd_path)
        new_files.append(core_file)
        
        # Core monitors
        core_mon_file = process_core_monitors(rtl_2xcd_path)
        new_files.append(core_mon_file)
        
        # Monitor SPI SQ trace
        spi_sq_file = process_monitor_spi_sq_trace(rtl_2xcd_path)
        new_files.append(spi_sq_file)
        
        # Monitor SQ inst trace
        sq_inst_file = process_monitor_sq_inst_trace(rtl_2xcd_path)
        new_files.append(sq_inst_file)
        
        # SQ monitor
        sq_mon_file = process_sq_monitor(rtl_2xcd_path)
        new_files.append(sq_mon_file)
        
        # SQ monitor SE SH CU
        se_sh_cu_file = process_sq_monitor_se_sh_cu(rtl_2xcd_path)
        new_files.append(se_sh_cu_file)
       
        sp_rtl_file = process_monitor_sp_rtl_trace(rtl_2xcd_path)#modify

        sp_itrace_file = process_sp_itrace_monitor_instance(rtl_2xcd_path)#modify
        
        # 4. Update rtl_2xcd.f
        update_rtl_2xcd_f(rtl_2xcd_path, new_files)
        
        print("\n[SUCCESS] All modifications completed")
        print(f"Generated files in: {rtl_2xcd_path}")
        print(f"Updated file list in: {dst_rtl_f}")
    
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
