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
args = parser.parse_args()


def print_child_elements(e):
    for ce in e.get_child_elements():
        print(ce.to_gedcom_string())
        print_child_elements(ce)


def get_quarter_date(text):
    year = text[3:7]
    match text[1:2]:
        case '1':
            return 'BET JAN ' + year + ' AND MAR ' + year
        case '2':
            return 'BET APR ' + year + ' AND JUN ' + year
        case '3':
            return 'BET JUL ' + year + ' AND SEP ' + year
        case '4':
            return 'BET OCT ' + year + ' AND DEC ' + year
        case _:
            print('BORKED')


def fix_name(e, ep):
    nick = ''
    suffix = ''
    prefix = ''
    for i in reversed(range(len(ep.get_child_elements()))):
        ec = ep.get_child_elements()[i]
        match ec.get_tag():
            case 'NICK':
                nick = ec.get_value()
            case 'POST':
                suffix = ec.get_value()
            case 'PREF':
                prefix = ec.get_value()
    if nick != '':
        e.add_child_element(Element(2, '', 'NICK', nick))
    if suffix != '':
        e.add_child_element(Element(2, '', 'NSFX', suffix))
        e.set_value(e.get_value() + ' ' + suffix)
    if prefix != '':
        e.add_child_element(Element(2, '', 'NPFX', prefix))


def fix_occupation(e):
    org = ""
    for i in reversed(range(len(e.get_child_elements()))):
        ec = e.get_child_elements()[i]
        match ec.get_tag():
            case 'TITL':
                e.set_value(ec.get_value() + e.get_value())
                e.get_child_elements().remove(ec)
            case 'ORG':
                org = ec.get_value() + ", "
                e.get_child_elements().remove(ec)
            case 'PLAC':
                ec.set_value(org + ec.get_value().strip())
            case _:
                process_generic_level_2_elements(e, i)
    e.set_value(e.get_value().strip())


def fix_residence(e):
    adr_elements = []
    for i in reversed(range(len(e.get_child_elements()))):
        ec = e.get_child_elements()[i]
        match ec.get_tag():
            case 'DWEL':
                adr_elements.append(ec.get_value())
                e.get_child_elements().remove(ec)
            case 'ROAD':
                adr_elements.append(ec.get_value() + ',')
                e.get_child_elements().remove(ec)
            case 'LOCA':
                adr_elements.append(ec.get_value() + ',')
                e.get_child_elements().remove(ec)
            case 'TOWN':
                adr_elements.append(ec.get_value() + ',')
                e.get_child_elements().remove(ec)
            case 'CO':
                adr_elements.append(ec.get_value() + ',')
                e.get_child_elements().remove(ec)
            case 'POST':
                adr_elements.append(ec.get_value() + ',')
                e.get_child_elements().remove(ec)
            case 'PLAC':
                adr_elements.append(ec.get_value() + ',')
                e.get_child_elements().remove(ec)
                # Should not have one of these from PEDIGREE but added for SCION
            case _:
                process_generic_level_2_elements(e, i)

    addr = Element(e.get_level() + 1, '', 'PLAC',
                   " ".join(reversed(adr_elements))[:-1])

    e.add_child_element(addr)


def process_generic_level_2_elements(ep, child_element_index):
    e = ep.get_child_elements()[child_element_index]
    global date_builder
    match e.get_tag():
        case 'DATE':
            if e.get_value().startswith('Q'):
                e.set_value(get_quarter_date(e.get_value()))
        case 'FROM':
            # Assumes FROM comes before TO
            from_prefix = ''
            if e.get_value().startswith('ABT'):
                from_prefix = ''
            else:
                from_prefix = 'from '
            date_builder = from_prefix + e.get_value() + date_builder
            ep.get_child_elements().remove(e)
        case 'TO':
            to_prefix = ''
            if e.get_value().startswith('ABT'):
                to_prefix = ''
            else:
                to_prefix = ' to ' + e.get_value()
            date_builder = date_builder + to_prefix
            ep.get_child_elements().remove(e)
        case 'CO':
            ep.add_child_element(Element(3, e.get_pointer(),
                                         'STAE', e.get_value()))
            ep.get_child_elements().remove(e)
        case 'PLAC':
            string_builder = ''
            for i in reversed(e.get_child_elements()):
                string_builder = ' | ' + i.get_value() + string_builder
                e.get_child_elements().remove(i)
            e.set_value(e.get_value() + string_builder)
        case 'PREF':
            # unknown tag - needs handling
            print("unknown tag: " + e.get_tag())
        case 'CONT':
            if len(e.get_value()) == 0:
                ep.get_child_elements().remove(e)
        case '_EVENTDETAIL':
            fixup = Element(2, '', 'NOTE', e.get_value())
            ep.get_child_elements()[child_element_index] = fixup
        case _:
            e.set_value(e.get_value().strip())


def debug(e):
    print(e.get_level())
    print(e.get_pointer())
    print(e.get_tag())
    print(e.get_value())
    if e.surname_match(''):  # Add surname to get more data from some records
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
gedcom_parser.parse_file(args.source_file)

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
                case 'NAME':
                    fix_name(ec, e)
                case 'NICK':
                    fixedElement.get_child_elements().remove(ec)
                case 'OCCU':
                    fix_occupation(ec)
                case 'RESI':
                    fix_residence(ec)
                case 'POST':
                    fixedElement.get_child_elements().remove(ec)
                case 'PREF':
                    fixedElement.get_child_elements().remove(ec)
                case _:
                    for k in reversed(range(len(ec.get_child_elements()))):
                        process_generic_level_2_elements(ec, k)
            if date_builder != '':
                if (date_builder.startswith('ABT') and
                        date_builder[3:].find(' to ') > 0):
                    to_loc = date_builder.find(' to ')
                    date_builder = 'BET' + date_builder[3:to_loc] \
                        + ' and ' + date_builder[to_loc + 4:]
                ec.add_child_element(Element(2, '', 'DATE',
                                             date_builder.strip()))
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
                case 'DIVO':
                    div = Element(ec.get_level(), '', 'DIV', '')
                    div.get_child_elements().extend(ec.get_child_elements())
                    e.add_child_element(div)
                    e.get_child_elements().remove(ec)
                case _:
                    for k in reversed(range(len(ec.get_child_elements()))):
                        process_generic_level_2_elements(ec, k)

output_file = open(args.target_file, "w")
gedcom_parser.save_gedcom(output_file)
