#!/bin/bash
# set -Eeuo pipefail
set -x
if [ -f "application.zip" ]
then
    rm application.zip
fi

if [ -d ".ebextensions" ]
then
    zip -r application.zip \
        bin \
        sql \
        static \
        templates \
        .env \
        application.py \
        config.py \
        Procfile \
        requirements.txt \
        .ebextensions
else
    zip -r application.zip \
        bin \
        sql \
        static \
        templates \
        .env \
        application.py \
        config.py \
        Procfile \
        requirements.txt
fi
