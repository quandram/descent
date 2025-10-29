import re
import shutil
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--sourceFile",
                    dest="source_file", help="source filename")
parser.add_argument("-t", "--targetFile",
                    dest="target_file", help="target filename")
args = parser.parse_args()

# work on a copy of the file to preserve the souce
shutil.copy(args.source_file, args.target_file)


def pre_process_line(line):
    appendToLine = "\n"
    if (line == "0 HEAD"):
        appendToLine = ""
    elif (line == "1 SYST"):
        appendToLine = ""
        line = ""
    elif (line == "2 SOUR Pedigree"):
        appendToLine = ""
        line = "\n1 SOUR Pedigree"
        line = line + "\n2 VERS 2.4L"
        line = line + "\n2 NAME Descent"
    elif (line == "2 DEST PAF"):
        appendToLine = ""
        line = "\n1 DEST GRAMPS"
        line = line + "\n1 SUBM @U1@"
        line = line + "\n1 GEDC"
        line = line + "\n2 VERS 5.5.1"
        line = line + "\n2 FORM LINEAGE-LINKED"
        line = line + "\n1 CHAR UTF-8"
    elif (line == "0 TRLR"):
        line = "0 @U1@ SUBM"
        line = line + "\n1 NAME Longman"
        line = line + "\n0 TRLR\n"

    if (line.startswith("0 @")):
        # @1@INDI -> @1@ INDI
        # @F1@FAM -> @F1@ FAM
        line = re.sub("0 @(.+?)@(\\S+?)", "0 @\\1@ \\2", line)
    # Remove I from individual record numbers:
    # @I1@INDI -> @1@ INDI | HUSB @I78@ -> HUSB @78@
    line = re.sub("@I(\\d+?)@", "@\\1@", line)
    return appendToLine + line


# some search and replace is required to make the file readable by the parser
with open(args.target_file, "r+") as f:
    lines = f.readlines()
    f.seek(0)
    f.truncate()
    for line in lines:
        f.write(pre_process_line(line.rstrip()))
