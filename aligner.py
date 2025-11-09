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


def process_element(e):
    if e.get_pointer() != "":
        print(e.get_pointer())
        fixedElement = Element(e.get_level(),
                               e.get_pointer()[0:2] +
                               "{:04d}".format(int(e.get_pointer()[2:-1])) +
                               '@', e.get_tag(), '')
        fixedElement.get_child_elements().extend(e.get_child_elements())
    else:
        fixedElement = e
    ec = fixedElement.get_child_elements()
    for j in reversed(range(len(ec))):
        c = ec[j]
        adjust_element(c, fixedElement)
    if args.should_alphabetise:
        ec.sort(key=elementSort)
    return fixedElement


def adjust_element(e, ep):
    is_deleted = False
    match e.get_tag():
        case 'DATE':
            date_parts = e.get_value().split(' ')
            for i in range(len(date_parts)):
                if len(date_parts[i]) == 1 and date_parts[i].isdigit():
                    date_parts[i] = "0" + date_parts[i]
            e.set_value(" ".join(date_parts).upper())
        case 'NAME':
            name_parts = e.get_value().split('/')
            if len(name_parts) > 1:
                name_parts[1] = name_parts[1].capitalize()
                post_spacing = ""
                if name_parts[2] != "":
                    post_spacing = " "
                e.set_value(name_parts[0] + ' /' +
                            name_parts[1] + '/' + post_spacing + name_parts[2])
        case 'GIVN':  # In Scion - not in Pedigree or Gramps
            ep.get_child_elements().remove(e)
            is_deleted = True
        case 'SURN':  # In Scion - not in Pedigree or Gramps
            ep.get_child_elements().remove(e)
            is_deleted = True
        case 'REFN':  # Random Scion reference
            ep.get_child_elements().remove(e)
            is_deleted = True
        case _:
            e.set_value(e.get_value().strip())
    if is_deleted is False:
        process_element(e)


# Initialize the parser and parse file
gedcom_parser = Parser()
gedcom_parser.parse_file(args.source_file)

l0_elements = gedcom_parser.get_root_child_elements()
# root_child_elements.sort(key=elementSort)

for i in reversed(range(len(l0_elements))):
    if isinstance(l0_elements[i], IndividualElement):
        l0_elements[i] = process_element(l0_elements[i])


output_file = open(args.target_file, "w")
gedcom_parser.save_gedcom(output_file)
