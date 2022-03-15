#!/bin/bash
set -Eeuo pipefail
set -x

./bin/manage_db.sh create
export FLASK_APP=application

usage() {
  echo "Usage: $0 (dev|prod)"
}
if [ $# -ne 1 ]; then
  usage
  exit 1
fi
# Parse argument.  $1 is the first argument
case $1 in
  "dev")
    export FLASK_ENV=development
    sed -i 's/application.run(debug=False)/application.run(debug=True)/' application.py
    python application.py
	;;
  "prod")
    export FLASK_ENV=production
    sed -i 's/application.run(debug=True)/application.run(debug=False)/' application.py
    uwsgi --http :8000 --wsgi-file application.py --master --processes 4 --threads 2
    ;;
  *)
    usage
    exit 1
    ;;
esac



