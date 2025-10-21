#!/usr/bin/env /tools/ctools/rh7.9/anaconda3/2023.03/bin/python3
# -*- coding: utf-8 -*-
"""
@Describe: Generate register address for stim.grbm_register
@Author: Lin Yiyu
Data: 2025.07.22
"""

import os, re, sys, argparse
from collections import OrderedDict
import glob

def parse_register(file_path):
    """parse register name and value from stim.grbm_register"""
    config_data = {
        'registers'     : OrderedDict(),
        'fields' : OrderedDict()
    }

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line =  line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                reg_name  = parts[0]

                if reg_name.endswith('_0'):
                    reg_name = reg_name[:-2] # hack for CP_HQD_*_0
                
                if len(parts) == 2:
                    # REG_NAME REG_VALUE
                    reg_value = parts[1]

                    if reg_value.startswith(('0x', '0X')):
                        hex_value = reg_value[2:] # remove 0x
                        bit_width = len(hex_value) * 4
                        config_data['registers'][reg_name] = f"{bit_width}'h{hex_value}"
                    else:
                        try:
                            value = int(reg_value)
                            config_data['registers'][reg_name] = f"32'h{value:08X}"
                        except ValueError:
                            config_data['registers'][reg_name] = reg_value;
                elif len(parts) == 5:
                    # REG_NAME FIELD_NAME CURRENT_OFFSET FIELD_VALUE FIELD_SIZE
                    field_name      = parts[1]
                    current_offset  = parts[2]
                    field_value     = parts[3]
                    field_size      = parts[4]
                    
                    if reg_name not in config_data['fields']:
                        config_data['fields'][reg_name] = []

                    if field_value.lower().startswith('0x'):
                        field_value = int(field_value, 16)
                    
                    if current_offset.lower().startswith('0x'):
                        current_offset = int(current_offset, 16)
                    if field_size.lower().startswith('0x'):
                        field_size = int(field_size, 16)

                    config_data['fields'][reg_name].append({
                        'field_name': field_name,
                        'offset':   current_offset,
                        'value':    field_value,
                        'size':     field_size
                    })
                else:
                    print(f"Warning: Invalid line format: {line}")  
        
        if not config_data['registers'] and not config_data['fields']:
            print(f"Warning: No valid configrations found in {file_path}")

        return config_data

    except Exception as e:
        print(f"Error parsing register file: {e}")
        return None

def parse_reg_map(file_path, required_regs):
    """parse register address from register_addr.v"""
    reg_map = {}
    pattern = re.compile(r'`define\s+(\w+)\s+(\d+)\'h([0-9a-fA-F]+)')

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    match =  pattern.match(line.strip())
                    if match:
                        reg_name  = match.group(1)
                        if reg_name in required_regs:
                            bit_width = match.group(2)
                            hex_value = match.group(3)
                            reg_map[reg_name] = f"{bit_width}'h{hex_value}"
        except Exception as e:
            print(f"Error parsing register file: {e}")

    if not reg_map: # search all file in dir
        dir_path = os.path.dirname(file_path)
        print(f"Scanning directory {dir_path} for register maapings")
        
        for reg_file in glob.glob(os.path.join(dir_path, '*')):
            try:
                with open(reg_file, 'r') as f:
                    for line in f:
                        match =  pattern.match(line.strip())
                        if match:
                            reg_name  = match.group(1)
                            if reg_name in required_regs:
                                bit_width = match.group(2)
                                hex_value = match.group(3)
                                reg_map[reg_name] = f"{bit_width}'h{hex_value}"
            except Exception as e:
                print(f"Error parsing register file: {e}")

    return reg_map

def generate_reg_map(config_data, reg_map, output_path):
    """Generate register mapping SystemVerilog out"""
    registers = config_data.get('registers', {})
    fields = config_data.get('fields', {})

    try:
        with open(output_path, 'w') as f:
            f.write("//// Auto-generated register mapping file \n")
            f.write("`ifndef GRBM_REGISTER_AUTO_CONFIG__SVH\n")
            f.write("`define GRBM_REGISTER_AUTO_CONFIG__SVH\n")

            f.write("virtual task automatic auto_config_registers(); \n")

            f.write("\n    // Register address mappings \n")
            for reg_name, reg_addr in reg_map.items():
                match = re.match(r"(\d+)'h([0-9a-fA-F]+)", reg_addr)
                if match:
                    bit_width = match.group(1)
                    hex_value = match.group(2)

                    f.write(f'    bit [31:0] ADDR_{reg_name} = {bit_width}\'h{hex_value};\n')

            f.write("\n    // Register values from stim.grbm_register \n")
            for reg_name, reg_value in registers.items():
                match = re.match(r"(\d+)'h([0-9a-fA-F]+)", reg_value)
                if match:
                    bit_width = match.group(1)
                    hex_value = match.group(2)

                    f.write(f'    bit [31:0] VALUE_{reg_name} = {bit_width}\'h{hex_value};\n')

            f.write("\n    // Auto-configuration task \n")
            f.write("    `uvm_info(get_type_name(), $psprintf(\"AUTO_CONFIG_REGISTERS TASK start\"), UVM_LOW); \n")                        
            for reg_name in registers:
                if reg_name in registers:
                    if reg_name in reg_map:
                        f.write(f"    write_register(ADDR_{reg_name}, VALUE_{reg_name}); // {reg_name} \n")
                    else:
                        f.write(f"    // Warning: Register {reg_name} NOT FOUND in reg_map!\n")

            for reg_name, field_list in fields.items():
              
                for field in field_list:
                    field_name = field['field_name']
                    offset = field['offset']
                    size = field['size']
                    value = field['value']
                    
                    mask = (1 << size) - 1
                    shifted_mask = mask << offset
                    shifted_value = value << offset
                    f.write(f"    write_register_with_mask(ADDR_{reg_name}, {shifted_value}, {shifted_mask}); // {reg_name} \n")

            f.write("    `uvm_info(get_type_name(), $psprintf(\"AUTO_CONFIG_REGISTERS TASK done\"), UVM_LOW); \n")
            f.write("endtask\n")
            f.write("`endif\n")

            print(f"Successfully generated {output_path}")
            return True
    except Exception as e:
        print(f"Error generating register map: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description = 'register mapping')
    parser.add_argument('testname', help='testname to find stim.grbm_register')

    args = parser.parse_args()

    input_file = f"../src/test/{args.testname}/stim.grbm_register"
    config_data = parse_register(input_file)
    registers = config_data.get('registers', {})
    fields = config_data.get('fields', {})

    map_file = "../../src/vega20c/common/pub/include/reg/register_addr.v"
    required_regs = list(registers.keys()) + list(fields.keys()) 
    reg_map = parse_reg_map(map_file, required_regs)

    output_file = "../src/testbench/performance/core/cache/sequence/grbm_register_auto_config.svh"
    generate_reg_map(config_data, reg_map, output_file)

if __name__ == "__main__":
    main()
