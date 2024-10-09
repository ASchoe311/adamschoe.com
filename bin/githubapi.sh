cd /var/app
projects=$(sqlite3 ./sql/db.sqlite "SELECT github_url FROM project" | python3 "geturllist.py")

urls=$(echo $projects | tr ";" "\n")

for addr in $urls
do
    echo "$addr"
    date=$(curl -s -L \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/ASchoe311/$addr/commits |\
  python3 -c "import sys, json, datetime; print(json.load(sys.stdin)[0]['commit']['committer']['date']);")
  echo "$date"
  sqlite3 ./sql/db.sqlite "UPDATE project SET lastupdate = '''$date''' WHERE github_url LIKE '%$addr%' LIMIT 1;"
done