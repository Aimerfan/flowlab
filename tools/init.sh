#!/bin/bash

set -e

sysctl -w vm.max_map_count=524288
