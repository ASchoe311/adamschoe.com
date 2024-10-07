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
        static \
        templates \
        .env \
        application.py \
        init.py \
        Procfile \
        requirements.txt \
        .ebextensions \
        .platform \
        public
else
    zip -r application.zip \
        bin \
        static \
        templates \
        .env \
        application.py \
        init.py \
        Procfile \
        requirements.txt \
        .platform \
        public
fi
