#!/bin/bash

set -e
set -o pipefail

sinter collect \
    --circuits out/circuits/*.stim \
    --metadata_func auto \
    --decoders pymatching \
    --max_shots 1_000_000 \
    --max_errors 100 \
    --processes 4 \
    --save_resume_filepath out/stats.csv \
    --postselected_detectors_predicate "len(coords) > 3 and coords[3] != 0"
