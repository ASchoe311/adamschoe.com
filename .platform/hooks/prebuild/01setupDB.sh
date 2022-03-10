#!/bin/bash

set -x

echo "CREATING DATABASE"

FILE=sql/db.sqlite3
  if test -f "$FILE"; then
  	echo "Error: database already exists"
  else
  	sqlite3 sql/db.sqlite3 < sql/schema.sql
  	sqlite3 sql/db.sqlite3 < sql/data.sql
fi