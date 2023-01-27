#!/bin/bash

set -e
set -o pipefail

# Chosen usage circuit.
PYTHONPATH=src parallel -q --ungroup tools/gen_circuits \
    --out_dir out/circuits \
    --distance 15 \
    --memory_rounds "d" \
    --postselected_rounds 2 \
    --postselected_diameter 5 7 \
    --noise_model SI1000 \
    --noise_strength {} \
    --basis hook_inject_X hook_inject_Y \
    ::: 0.0001 0.0002 0.0003 0.0005 0.0007 0.001 0.002 0.003 0.005 0.01


# Pareto curve frontier circuits.
PYTHONPATH=src parallel -q --ungroup tools/gen_circuits \
    --out_dir out/circuits \
    --distance 15 \
    --memory_rounds "d" \
    --postselected_rounds 1 2 3 4 5 6 \
    --postselected_diameter {} \
    --noise_model SI1000 \
    --noise_strength 0.001 \
    --basis li_inject_Y_magic_verify zz_inject_Y_magic_verify zz_tweaked_inject_Y_magic_verify hook_inject_Y_magic_verify \
    ::: 2 3 4 5 6 7
PYTHONPATH=src parallel -q --ungroup tools/gen_circuits \
    --out_dir out/circuits \
    --distance 15 \
    --memory_rounds "d" \
    --postselected_rounds 1 2 3 4 5 6 \
    --postselected_diameter {} \
    --noise_model SI1000 \
    --noise_strength 0.001 \
    --basis pregrown_hook_inject_Y_magic_verify \
    ::: 2 3 4 5 6 7 8 9 10 11
