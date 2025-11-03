from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from gedcom.element.element import Element
from gedcom.parser import Parser
import gedcom.tags
import re
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--sourceFile",
                    dest="source_file", help="source filename")
parser.add_argument("-t", "--targetFile",
                    dest="target_file", help="target filename")
# useful for checking changes to disable alphabetising:
parser.add_argument("-a", "--alpha", dest="should_alphabetise",
                    help="should alphabetise", default=False)
args = parser.parse_args()


def elementSort(e):
    return e.get_tag()


def adjust_value(e):
    match e.get_tag():
        case 'DATE':
            return e.get_value().upper()
        case _:
            return e.get_value()


# Initialize the parser and parse file
gedcom_parser = Parser()
gedcom_parser.parse_file(args.source_file)

l0_elements = gedcom_parser.get_root_child_elements()
# root_child_elements.sort(key=elementSort)

for i in reversed(range(len(l0_elements))):
    e = l0_elements[i]
    if isinstance(e, IndividualElement):
        l1_elements = e.get_child_elements()
        for j in reversed(range(len(l1_elements))):
            l1 = l1_elements[j]
            l1_elements[j].set_value(adjust_value(l1_elements[j]))
            l2_elements = l1.get_child_elements()
            for k in reversed(range(len(l2_elements))):
                l2 = l2_elements[k]
                l2_elements[k].set_value(adjust_value(l2))
            if args.should_alphabetise:
                l2_elements.sort(key=elementSort)
            l1_elements[j].child_elements = l2_elements
        if args.should_alphabetise:
            l1_elements.sort(key=elementSort)
        l0_elements[i].child_elements = l1_elements

output_file = open(args.target_file, "w")
gedcom_parser.save_gedcom(output_file)
