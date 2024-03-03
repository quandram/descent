from gedcom.element.individual import IndividualElement
from gedcom.element.element import Element
from gedcom.parser import Parser
import gedcom.tags

# Path to your `.ged` file
source_file = './data/DEV_1_OUTPUT.GED'
target_file = './data/DEV_2_OUTPUT.GED'


def print_child_elements(e):
    for ce in e.get_child_elements():
        print(ce.to_gedcom_string())
        print_child_elements(ce)


def fix_occupation(e):
    for i in reversed(range(len(e.get_child_elements()))):
        ec = e.get_child_elements()[i]
        match ec.get_tag():
            case 'TITL':
                e.set_value(ec.get_value())
                e.get_child_elements().remove(ec)
            case _:
                process_generic_level_2_elements(e, i)


def process_generic_level_2_elements(ep, child_element_index):
    e = ep.get_child_elements()[child_element_index]
    match e.get_tag():
        case 'FROM' | 'TO' | 'ORG' | 'DWEL' | 'LOCA' | 'TOWN' | 'CO' | 'ROAD' | 'CONT' | 'COUN' | 'PREF' | 'DIVO':
            # unknown tag - needs handling
            print("unknown tag")
            a = Element(2,'A1','WOOT','VFT') #replace tag with something else
            ep.get_child_elements()[child_element_index] = a


def debug(e):
    print(e.get_level())
    print(e.get_pointer())
    print(e.get_tag())
    print(e.get_value())
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
        for x in e.get_child_elements():
            if x.get_tag() == gedcom.tags.GEDCOM_TAG_OCCUPATION:
                print_child_elements(x)


# Initialize the parser and parse file
gedcom_parser = Parser()
gedcom_parser.parse_file(source_file)

root_child_elements = gedcom_parser.get_root_child_elements()

for i in reversed(range(len(root_child_elements))):
    e = root_child_elements[i]
    if isinstance(e, IndividualElement):
        debug(e)
        fixedElement = Element(0,'@I' + e.get_pointer()[1:-1] + '@', 'INDI', '')
        fixedElement.get_child_elements().extend(e.get_child_elements())
        for ec in e.get_child_elements():
            match ec.get_tag():
                case 'OCCU':
                    fix_occupation(ec)
                case _:
                    print('no special handling')
                    for i in reversed(range(len(ec.get_child_elements()))):
                        process_generic_level_2_elements(ec, i)
        root_child_elements[i] = fixedElement

output_file = open(target_file, "w")
gedcom_parser.save_gedcom(output_file)
