import sys

projects = ""
for url in sys.stdin.readlines():
    proj = url.split("/")[-1][:-1]
    projects += proj + ";"

print(projects)



