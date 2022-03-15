#!/bin/bash

set -x
$(./bin/allunix.sh)
echo $(eb deploy)
