import re
import shutil

# Path to your `.ged` file
source_file = './data/LONGMAN.GED'
target_file = './data/LONGMAN_1_OUTPUT.GED'

# work on a copy of the file to preserve the souce
shutil.copy(source_file, target_file)

def pre_process_line(l):
    appendToLine = "\n"
    if (l == "0 HEAD"):
        appendToLine = ""
    elif (l == "1 SYST"):
        appendToLine = ""
        l = ""
    elif (l == "2 SOUR Pedigree"):
        appendToLine = ""
        l = "\n1 SOUR Pedigree"
        l = l + "\n2 VERS 2.4L"
        l = l + "\n2 NAME Descent"
    elif (l == "2 DEST PAF"):
        appendToLine = ""
        l = "\n1 DEST GRAMPS"
        l = l + "\n1 SUBM Longman"
        l = l + "\n1 GEDC"
        l = l + "\n2 VERS 5.5.1"
        l = l + "\n2 FORM LINEAGE-LINKED"
        l = l + "\n1 CHAR UTF-8"

    if (l.startswith("0 @")):
        # @1@INDI -> @1@ INDI
        # @F1@FAM -> @F1@ FAM
        l = re.sub("0 @(.+?)@(\\S+?)", "0 @\\1@ \\2", l)
    # Remove I from individual record numbers: @I1@INDI -> @1@ INDI | HUSB @I78@ -> HUSB @78@
    l = re.sub("@I(\\d+?)@", "@\\1@", l)
    return appendToLine + l

# some search and replace is required to make the file readable by the parser
with open(target_file, "r+") as f:
    lines = f.readlines()
    f.seek(0)
    f.truncate()
    for l in lines:
        f.write(pre_process_line(l.rstrip()))
