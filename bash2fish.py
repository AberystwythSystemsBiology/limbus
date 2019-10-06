import re

fish = ""

with open("helpers.sh", "r") as infile:
    for line in infile.readlines():
        line = re.sub("/bin/bash", "/bin/fish", line)

        line = re.sub("[{()]", "", line)
        line = re.sub("[}]", "end", line)
        fish += "%s" % (line)

with open("helpers.fish", "w") as outfile:
    outfile.writelines(fish)