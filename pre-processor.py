import re
import shutil

# Path to your `.ged` file
source_file = './data/LONGMAN.GED'
target_file = './data/LONGMAN_1_OUTPUT.GED'

# work on a copy of the file to preserve the souce
shutil.copy(source_file, target_file)

def pre_process_line(l):
    if (l.startswith("0 @")):
        # - @1@INDI -> @1@ INDI
        # - @F1@FAM -> @F1@ FAM
        return re.sub("0 @(.+?)@(\\S+?)", "0 @\\1@ \\2", l)
    return l

# some search and replace is required to make the file readable by the parser
with open(target_file, "r+") as f:
    ll = f.readlines()
    f.seek(0)
    f.truncate()
    for l in ll:
        f.write(pre_process_line(l))
