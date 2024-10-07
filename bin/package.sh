#!/bin/bash
# set -Eeuo pipefail
set -x
if [ -f "application.zip" ]
then
    rm application.zip
fi

sed -i 's/application.run(debug=True)/application.run(debug=False)/' application.py
sed -i "s/sqlite:\/\/\/.\/sql\/db.sqlite/sqlite:\/\/\/..\/sql\/db.sqlite/" init.py
sed -i -e "s/static/\.\./" init.py

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
