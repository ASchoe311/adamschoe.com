#!/bin/bash

for file in $(find . -name '*.sh')
do
  $(dos2unix "$file")
done
