#!/bin/bash

for file in $(find bin -name '*.sh')
do
  $(dos2unix "$file")
done
for file in $(find .platform -name '*.sh')
do
  $(dos2unix "$file")
done
for file in $(find .ebextensions -name '*.config')
do
  $(dos2unix "$file")
done