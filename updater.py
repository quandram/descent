from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from gedcom.element.element import Element
from gedcom.parser import Parser
import gedcom.tags
import re

# Path to your `.ged` file
source_file = './data/LONGMAN_1_OUTPUT.GED'
target_file = './data/LONGMAN_2_OUTPUT.GED'


def print_child_elements(e):
    for ce in e.get_child_elements():
        print(ce.to_gedcom_string())
        print_child_elements(ce)


def fix_occupation(e):
    for i in reversed(range(len(e.get_child_elements()))):
        ec = e.get_child_elements()[i]
        match ec.get_tag():
            case 'TITL':
                e.set_value(ec.get_value() + e.get_value())
                e.get_child_elements().remove(ec)
            case 'ORG':
                e.set_value(e.get_value() + " @ " + ec.get_value())
                e.get_child_elements().remove(ec)
            case _:
                process_generic_level_2_elements(e, i)


def fix_residence(e):
    for i in reversed(range(len(e.get_child_elements()))):
        ec = e.get_child_elements()[i]
        match ec.get_tag():
            case 'DWEL':
                e.get_child_elements()[i] = Element(2, '', 'ADDR',
                                                    ec.get_value())
            case 'ROAD':
                e.get_child_elements()[i] = Element(2, '', 'ADDR',
                                                    ec.get_value())
            case 'TOWN':
                e.get_child_elements()[i] = Element(2, '', 'PLAC',
                                                    ec.get_value())
            case _:
                process_generic_level_2_elements(e, i)


def process_generic_level_2_elements(ep, child_element_index):
    e = ep.get_child_elements()[child_element_index]
    global date_builder
    match e.get_tag():
        case 'FROM':
            date_builder = 'from ' + e.get_value() + date_builder
            ep.get_child_elements().remove(e)
        case 'TO':
            date_builder = date_builder + ' to ' + e.get_value()
            ep.get_child_elements().remove(e)
        case 'LOCA' | 'CO' | 'PREF' | 'DIVO':
            # unknown tag - needs handling
            print("unknown tag: " + e.get_tag())


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
        # debug(e)
        fixedElement = Element(0, '@I' + e.get_pointer()[1:-1] + '@', 'INDI',
                               '')
        fixedElement.get_child_elements().extend(e.get_child_elements())
        for j in reversed(range(len(e.get_child_elements()))):
            ec = e.get_child_elements()[j]
            global date_builder
            date_builder = ''
            match ec.get_tag():
                case 'OCCU':
                    fix_occupation(ec)
                case 'RESI':
                    fix_residence(ec)
                case _:
                    print('no special handling')
                    for k in reversed(range(len(ec.get_child_elements()))):
                        process_generic_level_2_elements(ec, k)
            if date_builder != '':
                ec.add_child_element(Element(2, '', 'DATE', date_builder))
        root_child_elements[i] = fixedElement
    if isinstance(e, FamilyElement):
        for j in reversed(range(len(e.get_child_elements()))):
            ec = e.get_child_elements()[j]
            match ec.get_tag():
                case 'HUSB':
                    ec.set_value(re.sub("@(.+?)@", "@I\\1@",
                                        ec.get_value()))
                case 'WIFE':
                    ec.set_value(re.sub("@(.+?)@", "@I\\1@",
                                        ec.get_value()))
                case 'CHIL':
                    ec.set_value(re.sub("@(.+?)@", "@I\\1@",
                                        ec.get_value()))
output_file = open(target_file, "w")
gedcom_parser.save_gedcom(output_file)
