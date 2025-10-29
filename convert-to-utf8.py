import codecs
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--sourceFile",
                    dest="source_file", help="source filename")
parser.add_argument("-t", "--targetFile",
                    dest="target_file", help="target filename")
args = parser.parse_args()

# Needed for pure Pedigree export
BLOCKSIZE = 1048576  # or some other, desired size in bytes
with codecs.open(args.source_file, "r", "ISO-8859-1") as sourceFile:
    with codecs.open(args.target_file, "w", "utf-8") as targetFile:
        while True:
            contents = sourceFile.read(BLOCKSIZE)
            if not contents:
                break
            targetFile.write(contents.replace('ISO-8859-1', 'utf-8'))
