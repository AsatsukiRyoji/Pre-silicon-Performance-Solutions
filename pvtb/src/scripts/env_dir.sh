#!/bin/bash
# Environment configuration file for cache regression
# This file sets up the basic environment variables and paths

# Set STEM environment variable if not already set
if [ -z "$STEM" ]; then
    export STEM=$(pwd)
fi

# Set output directory - will be substituted with actual out_path
export OUT_DIR=out

# Set up common paths
export PVTB_DIR=$STEM/pvtb
export SRC_DIR=$PVTB_DIR/src
export TEST_DIR=$SRC_DIR/test
export SHELLS_DIR=$SRC_DIR/gkt/shells
export METHODOLOGY_DIR=$SRC_DIR/methology

# Set up compilation paths
export COMPILE_DIR=$OUT_DIR/compile/cache_sanity_test
export RUN_DIR=$OUT_DIR/run

# Set up report paths
export REGRESS_REPORT_DIR=regress_report

# Create necessary directories
mkdir -p $COMPILE_DIR
mkdir -p $RUN_DIR
mkdir -p $REGRESS_REPORT_DIR

echo "Environment configured:"
echo "  STEM: $STEM"
echo "  OUT_DIR: $OUT_DIR"
echo "  COMPILE_DIR: $COMPILE_DIR"
echo "  RUN_DIR: $RUN_DIR"
echo "  REGRESS_REPORT_DIR: $REGRESS_REPORT_DIR"
