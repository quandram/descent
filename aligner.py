from gedcom.element.individual import IndividualElement
from gedcom.element.element import Element
from gedcom.parser import Parser
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


def process_element(e, process_pointer=False):
    if process_pointer and e.get_pointer() != "":
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
            # pad day values to 2 digits
            # upper case month values
            date_parts = e.get_value().split(' ')
            for i in range(len(date_parts)):
                if len(date_parts[i]) == 1 and date_parts[i].isdigit():
                    date_parts[i] = "0" + date_parts[i]
            e.set_value(" ".join(date_parts).upper())
        case 'NAME':
            # Fix forced upper case surname SCION did
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
        case 'REFN':  # Unnecessary Scion reference
            ep.get_child_elements().remove(e)
            is_deleted = True
        case 'PEDI':  # Unnecessary
            ep.get_child_elements().remove(e)
            is_deleted = True
        case 'NOTE':
            # Retrieve NOTE content from footer
            if e.get_value()[0:1] == '@' and e.get_value()[-1]:
                for i in range(len(l0_elements)):
                    note_ref = l0_elements[i]
                    if note_ref.get_pointer() == e.get_value():
                        e.set_value(note_ref.get_value())
                        if len(note_ref.get_child_elements()) > 0:
                            for j in range(len(note_ref.get_child_elements())):
                                note_child = note_ref.get_child_elements()[j]
                                e.new_child_element(
                                    note_child.get_tag(), "", note_child.get_value())
        case _:
            e.set_value(e.get_value().strip())
    if is_deleted is False:
        process_element(e)


# Initialize the parser and parse file
gedcom_parser = Parser()
gedcom_parser.parse_file(args.source_file)

l0_elements = gedcom_parser.get_root_child_elements()

for i in reversed(range(len(l0_elements))):
    # l0_elements[i] = process_element(
    #    l0_elements[i], isinstance(l0_elements[i], IndividualElement))
    l0_elements[i] = process_element(l0_elements[i])

# Strip referenced note elements after processing
for i in reversed(range(len(l0_elements))):
    if l0_elements[i].get_tag() == "NOTE":
        gedcom_parser.get_root_child_elements().remove(l0_elements[i])

output_file = open(args.target_file, "w")
gedcom_parser.save_gedcom(output_file)
