#!/bin/bash

# Stop on errors
# See https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -Eeuo pipefail
# Sanity check command line options
usage() {
  echo "Usage: $0 (create|destroy|reset|dump)"
}
if [ $# -ne 1 ]; then
  usage
  exit 1
fi
# Parse argument.  $1 is the first argument
case $1 in
  "create")
	  FILE=sql/db.sqlite
	  if test -f "$FILE"; then
	  	echo "Error: database already exists"
	  else
	  	sqlite3 sql/db.sqlite < sql/schema.sql
	  	sqlite3 sql/db.sqlite < sql/data.sql
    fi
	;;
  "destroy")
    rm -rf sql/db.sqlite
    ;;
  "reset")
    rm -rf sql/db.sqlite
	  sqlite3 sql/db.sqlite < sql/schema.sql
	  sqlite3 sql/db.sqlite < sql/data.sql
    ;;
  "dump")
	  tablesStr=$(<. sqlite3 sql/db.sqlite '.tables')
	  IFS='\' read -r -a tables <<< "$tablesStr"
	  # echo ${tables[@]}
    for table in ${tables}
	  do
	  	sqlite3 -batch -line sql/db.sqlite "SELECT * FROM $table"
	  	echo
	  done
    ;;
  *)
    usage
    exit 1
    ;;
esac
