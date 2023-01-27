#!/bin/bash

set -e
set -o pipefail

mkdir -p out/plot


# Pareto frontier plot.
./tools/plot_pareto_curves \
    --gates cz \
    --stats out/stats.csv \
    --out out/plot/frontier.png &


# Expected usage plot.
./tools/plot_expected_usage_plot \
    --stats out/stats.csv \
    --out out/plot/expected_usage.png &


wait
echo "wrote files:"
echo "    out/plot/frontier.png"
echo "    out/plot/expected_usage.png"
