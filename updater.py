from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser
import gedcom.tags

# Path to your `.ged` file
file_path = './data/DEV.GED'
file_output_path = './data/DEV_OUTPUT.GED'


def print_child_elements(e):
    for ce in e.get_child_elements():
        print(ce.to_gedcom_string())
        print_child_elements(ce)


def debug(e):
    if e.surname_match('Longman'):
        # Unpack the name tuple
        (first, last) = e.get_name()
        occ = e.get_occupation()
        name = first + " " + last
        parentsNames = ""
        try:
            (p1, p2) = gedcom_parser.get_parents(e)
            (p1f, p1l) = p1.get_name()
            (p2f, p2l) = p2.get_name()
            parentsNames = p1f + " " + p1l + " / " + p2f + " " + p2l
        except (ValueError):
            print("Can't get parents of: " + name)
        print(name + ": " + parentsNames + " - " + occ)
        # print_child_elements(element)
        for x in e.get_child_elements():
            if x.get_tag() == gedcom.tags.GEDCOM_TAG_OCCUPATION:
                print_child_elements(x)


def fix_occupation(e):
    for ec in e.get_child_elements():
        match ec.get_tag():
            case 'TITL':
                e.set_value(ec.get_value())
                e.get_child_elements().remove(ec)
            case _:
                print(type(ec))
                print(ec)


# Initialize the parser
gedcom_parser = Parser()

# Parse your file
gedcom_parser.parse_file(file_path)
root_child_elements = gedcom_parser.get_root_child_elements()

for e in root_child_elements:

    if isinstance(e, IndividualElement):
        debug(e)

        for ec in e.get_child_elements():
            match ec.get_tag():
                case 'OCCU':
                    fix_occupation(ec)
                case _:
                    print('no special handling')

output_file = open(file_output_path, "w")
# gedcom_parser.print_gedcom()
gedcom_parser.save_gedcom(output_file)
