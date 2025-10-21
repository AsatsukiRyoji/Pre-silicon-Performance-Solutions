#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Describe: lds 64 bank
@Author: Guo Shihao
Data: 2025.07.26
"""

import os, pdb, sys
cdir = os.path.dirname(os.path.realpath(__file__)) + '/'

class BackDoor():
    def __init__(self):
        self.se = 4
        self.sh_per_se = 1
        self.cu_per_sh = 12
        self.sp = 2
        self.vgpr_simd = 2
        self.vgpr_simd_bank = 4
        self.sgpr_simd = 4
        self.lds_bank_per_cu = 64
        self.initial_str_cont = '''// ============================================================================ //
//  Copyright (c) 2009-2016 Advanced Micro Devices, Inc.  All rights reserved.  //
// ============================================================================ //
// Backdoor load SP0/SP1/SQ/LDS memories if run_time arg "backdoor_sh_mem=on" is present
integer test_seed;

reg backdoor_sh_mem_enabled;

localparam backdoor_sh_mem = "backdoor_sh_mem=";

initial begin
  if(!$value$plusargs("seed=%d",test_seed))
     test_seed = test_seed;

  if($test$plusargs({backdoor_sh_mem,"on"}))
     backdoor_sh_mem_enabled = 1;
end

`ifdef THIS_IS_REALLY_NOT_DEFINED_OKAY
function bit [31:0]  GetRand32();
  bit [31:0]  rand_value;
  test_seed = (test_seed*longint'(214013) + longint'(2531011)) & 32'hffffffff;
  rand_value = test_seed;
  return (rand_value);
endfunction

function bit [127:0] GetRand128();
  bit [127:0] rand_value128;
  rand_value128 = (GetRand32() << 96) | (GetRand32() << 64) | (GetRand32() << 32) | GetRand32(); 
  return (rand_value128);
endfunction
`endif
        '''
        self.vgpr_str_cont = '''
integer vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s;

always @(posedge resetb) begin
if (backdoor_sh_mem_enabled == 1) begin
  `MSGIO_DISPLAY("*I : SH memories se%s_sh%s_cu%s_sp%s_simd%s_bank%s are being backdoor loaded");
  //-- Backdoor load SP VGPR ATI_IMEM_BFM memories
  for( vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s = 0; 
       vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s < `GPU__SP__NUM_GPRS; 
       vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s =
       vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s + 1 )
  begin

`ifdef CORE_TILE
     `define TMPMEM     `TB__SE%s__SH%s__SP%s_%s__SP_SIMD%s_TOP.usp_simd%s.usp_gpr_bank%s.usp_cmem2p256x128b8qaioue1_k4
     `define TMPMEM_ODD `TB__SE%s__SH%s__SP%s_%s__SP_SIMD%s_TOP.usp_simd%s.usp_gpr_bank%s.usp_cmem2p256x128b8qaioue1_k4_odd
`else
     `define TMPMEM     `TB__SE%s__SH%s__SP%s_%s.sp_simd%s_top.usp_simd%s.usp_gpr_bank%s.usp_cmem2p256x128b8qaioue1_k4
     `define TMPMEM_ODD `TB__SE%s__SH%s__SP%s_%s.sp_simd%s_top.usp_simd%s.usp_gpr_bank%s.usp_cmem2p256x128b8qaioue1_k4_odd     
`endif //CORE_TILE

     if( `TMPMEM.RSTA !== 1'b0 )
     begin
       @( negedge `TMPMEM.RSTA );
       @( negedge `TMPMEM.CLKA );
       //`MSGIO_DISPLAY
       //  ( "Saw negedge of RSTA, will now load SP GPRs..." );
     end
     `TMPMEM.write( vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s, {4{32'hbdbdbdbd}}, {4{32'hbdbdbdbd}}, {4{32'hbdbdbdbd}}, {4{32'hbdbdbdbd}} );
     `TMPMEM_ODD.write( vgpr_se%s_sh%s_cu%s_sp%s_simd%s_bank%s, {4{32'hbdbdbdbd}}, {4{32'hbdbdbdbd}}, {4{32'hbdbdbdbd}}, {4{32'hbdbdbdbd}} );     
     `undef TMPMEM
     `undef TMPMEM_ODD
  end //-- vgpr_addr for loop
end //-- if backdoor_sh_mem_enabled
end //-- always @
  '''
        self.lds_str_cont = '''
integer lds_se%s_sh%s_cu%s_bank%s;

always @(posedge resetb) begin
if (backdoor_sh_mem_enabled == 1) begin
  //-- Backdoor load LDS memories
  for( lds_se%s_sh%s_cu%s_bank%s = 0;
       lds_se%s_sh%s_cu%s_bank%s < 1024;
       lds_se%s_sh%s_cu%s_bank%s = 
       lds_se%s_sh%s_cu%s_bank%s + 1) begin
     
     `define TMPMEM `TB__SE%s__SH%s__LDS%s.ds.ds_lds_mem.bank%s
    
     if( `TMPMEM.RSTA !== 1'b0 )
     begin
       @( negedge `TMPMEM.RSTA );
       @( negedge `TMPMEM.CLKA );
       `MSGIO_DISPLAY
         ( "Saw negedge of RSTA, will now backdoor load LDS memories lds_se%s_sh%s_cu%s_bank%s" );
     end

     `TMPMEM.write( lds_se%s_sh%s_cu%s_bank%s, 33'h0fefefefe );

     `undef TMPMEM
  end //-- lds_addr for loop
end
end
        '''
        self.sgpr_str_cont = '''
integer sgpr_se%s_sh%s_cu%s_simd%s;

always @(posedge resetb) begin
if (backdoor_sh_mem_enabled == 1) begin
  //-- Backdoor load SQ SGPR memories
  //FIXME for(sgpr_addr=0; sgpr_addr<`GPU__GC__NUM_SGPR_PER_SIMD; sgpr_addr=sgpr_addr+1) begin
  for( sgpr_se%s_sh%s_cu%s_simd%s=0;
       sgpr_se%s_sh%s_cu%s_simd%s < 200; 
       sgpr_se%s_sh%s_cu%s_simd%s =
       sgpr_se%s_sh%s_cu%s_simd%s + 1 ) begin

      `define TMPMEM `TB__SE%s__SH%s__SQ%s.ex.sgpr.mem%s

      if( `TMPMEM.RSTA !== 1'b0 )
      begin
        @( negedge `TMPMEM.RSTA );
        @( negedge `TMPMEM.CLKA );
        `MSGIO_DISPLAY
          ( "Saw negedge of RSTA, will now load SGPRs..." );
      end

      `TMPMEM.write( sgpr_se%s_sh%s_cu%s_simd%s, {4{32'hbdbdbdbd}} );

      `undef TMPMEM
  end //-- sgpr_addr for loop
end
end
    '''
        self.m0_str_cont = '''
integer m0_se%s_sh%s_cu%s_simd%s;

always @(posedge resetb) begin
if (backdoor_sh_mem_enabled == 1) begin

  for( m0_se%s_sh%s_cu%s_simd%s = 0;
       m0_se%s_sh%s_cu%s_simd%s < 10;
       m0_se%s_sh%s_cu%s_simd%s = 
       m0_se%s_sh%s_cu%s_simd%s + 1 ) begin

      `define TMPMEM `TB__SE%s__SH%s__SQ%s.ex.sreg.m0_mem%s

      if( `TMPMEM.RSTA !== 1'b0 )
      begin
        @( negedge `TMPMEM.RSTA );
        @( negedge `TMPMEM.CLKA );
        `MSGIO_DISPLAY
          ( "Saw negedge of RSTA, will now load M0 rams..." );
      end

      `TMPMEM.write( m0_se%s_sh%s_cu%s_simd%s, 32'h0 );
      `undef TMPMEM
  end // for
end // if
end // always
    '''
        self.end_str_cont = '''
always @(posedge resetb) begin
  if (backdoor_sh_mem_enabled == 1) begin
    `MSGIO_DISPLAY("*I : SH bfm memories are being backdoor loaded");
  end
  else begin
    `MSGIO_DISPLAY("*I : SH bfm memories are NOT being backdoor loaded");
  end
end //--always @(posedge resetb)
    '''

    def vgpr_add_odd(self):
        with open('tb_ld_sh_mem_gen.svh', 'a') as f:
            f.write(self.initial_str_cont)
            for i in range(self.se):
                for j in range(self.sh_per_se):
                    for k in range(self.cu_per_sh):
                        for m in range(self.sp):
                            for n in range(self.vgpr_simd):
                                for o in range(self.vgpr_simd_bank):
                                    f.write(self.vgpr_str_cont%(i,j,k,m,n,o,\
                                            i,j,k,m,n,o,\
                                            i,j,k,m,n,o,\
                                            i,j,k,m,n,o,\
                                            i,j,k,m,n,o,\
                                            i,j,k,m,n,o,\
                                            i,j,k,m,2*m+n,2*m+n,o,\
                                            i,j,k,m,2*m+n,2*m+n,o,\
                                            i,j,k,m,2*m+n,2*m+n,o,\
                                            i,j,k,m,2*m+n,2*m+n,o,\
                                            i,j,k,m,n,o,\
                                            i,j,k,m,n,o,\
                                            ));

    def lds_mem_64(self):
        with open('tb_ld_sh_mem_gen.svh', 'a') as f:
            for i in range(self.se):
                for j in range(self.sh_per_se):
                    for k in range(self.cu_per_sh):
                        for m in range(self.lds_bank_per_cu):
                            f.write(self.lds_str_cont%(i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    ));

    def sgpr_ori(self):
        with open('tb_ld_sh_mem_gen.svh', 'a') as f:
            for i in range(self.se):
                for j in range(self.sh_per_se):
                    for k in range(self.cu_per_sh):
                        for m in range(self.sgpr_simd):
                            f.write(self.sgpr_str_cont%(i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    ));

    def m0_ori(self):
        with open('tb_ld_sh_mem_gen.svh', 'a') as f:
            for i in range(self.se):
                for j in range(self.sh_per_se):
                    for k in range(self.cu_per_sh):
                        for m in range(self.sgpr_simd):
                        #for m in range(self.lds_bank_per_cu):
                            f.write(self.m0_str_cont%(i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    i,j,k,m,\
                                    ));
            f.write(self.end_str_cont)

    def all_str_write(self):
        self.vgpr_add_odd()
        self.lds_mem_64()
        self.sgpr_ori()
        self.m0_ori()


if __name__ == "__main__":
    bd = BackDoor()
    bd.all_str_write()

