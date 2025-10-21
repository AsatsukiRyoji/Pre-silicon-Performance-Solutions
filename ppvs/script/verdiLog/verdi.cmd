wvCreateWindow
simSetSimulator "-vcssv" -exec \
           "/project/hawaii/a0/archbox1/jiangxiaofei/pvtb_0921/out/compile/cache_sanity_test/simv" \
           -args
debImport "-dbdir" \
          "/project/hawaii/a0/archbox1/jiangxiaofei/pvtb_0921/out/compile/cache_sanity_test/simv.daidir"
srcFndSigCreate
srcFndSignalSearch -delim "." -case on -fullHierarchy off -libcell off -name \
           "tb.*spi_cpc_eos*"
srcFndInstCreate
srcFndInstSearch -delim "." -case on -fullHierarchy off -libcell off -name \
           "tb.*spi_cpc_eos*"
srcShowCalling "tb.if_spi_cpc_eos_die0_pipe1" -win $_nTrace1
srcSelect -win $_nTrace1 -range {7 7 3 4 1 1}
srcHBSelect "tb" -win $_nTrace1
verdiWindowResize -win $_Verdi_1 "125" "107" "1277" "743"
srcDeselectAll -win $_nTrace1
srcSelect -word -line 6 -pos 2 -win $_nTrace1
srcDeselectAll -win $_nTrace1
srcSelect -word -line 11 -pos 2 -win $_nTrace1
srcDeselectAll -win $_nTrace1
srcSelect -word -line 13 -pos 2 -win $_nTrace1
srcDeselectAll -win $_nTrace1
srcSelect -win $_nTrace1 -signal "tb.core.gc.se1.spi.SPI_SQ0_cmd_valid" -line 28 \
          -pos 1
srcDeselectAll -win $_nTrace1
srcSelect -win $_nTrace1 -signal "tb.core.gc.se1.spi.SPI_SQ0_cmd_valid" -line 28 \
          -pos 1
srcDeselectAll -win $_nTrace1
srcSelect -win $_nTrace1 -signal "tb.core.gc.se1.spi.SPI_SQ0_cmd_valid" -line 28 \
          -pos 1
srcAction -pos 27 1 23 -win $_nTrace1 -name \
          "tb.core.gc.se1.spi.SPI_SQ0_cmd_valid" -ctrlKey off
srcBackwardHistory -win $_nTrace1
srcHBSelect "tb" -win $_nTrace1
