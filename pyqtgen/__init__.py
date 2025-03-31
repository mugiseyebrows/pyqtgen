import os
import xml.etree.ElementTree as ET
import argparse

RULE = """
rule uic
    command = pyside6-uic $in -o $out
rule rcc
    command = pyside6-rcc $in -o $out
"""

def get_class(path):
    tree = ET.parse(path)
    root = tree.getroot()
    item = root.find('class')
    return item.text

def replace_ext(path, ext):
    return os.path.splitext(path)[0] + ext

def ninja():
    basedir = os.getcwd()
    with open(os.path.join(basedir, 'build.ninja'), 'w', encoding='utf-8') as file:
        file.write(RULE)
        for root, dirs, files in os.walk(basedir):
            for f in files:
                name, ext = os.path.splitext(f)
                if ext == '.ui':
                    p = os.path.join(root, f)
                    c = get_class(p)
                    src = os.path.relpath(p, basedir)
                    dst = os.path.relpath(os.path.join(root, "Ui_{}.py".format(c)))
                    file.write("build {}: uic {}\n".format(dst, src))
                elif ext == '.qrc':
                    p = os.path.join(root, f)
                    src = os.path.relpath(p, basedir)
                    dst = replace_ext(src, '.py')
                    file.write("build {}: rcc {}\n".format(dst, src))


def qrc_init(qrc_path):
    if os.path.exists(qrc_path):
        return
    with open(qrc_path, "w", encoding='utf-8') as f:
        print("<RCC></RCC>", file=f)

def find_qresource(root, prefix):
    for qresource in root.findall('qresource'):
        if qresource.attrib['prefix'] == prefix:
            return qresource

def qrc_add(qrc_path, paths, prefix = None, alias = None):
    qrc_init(qrc_path)
    if prefix is None:
        prefix = "/"
    tree = ET.parse(qrc_path)
    root = tree.getroot()

    qresource = find_qresource(root, prefix)
    if qresource is None:
        qresource = ET.Element('qresource', {'prefix': prefix})
        root.append(qresource)

    for path in paths:
        attrib = {}
        if alias:
            attrib['alias'] = alias
        file = ET.Element('file', attrib)
        file.text = path.replace("\\", "/")
        qresource.append(file)

    tree.write(qrc_path, encoding='utf-8')    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['qrc-add', 'ninja'], nargs='?', default='ninja')
    parser.add_argument('path', nargs='*')
    parser.add_argument('-a', '--alias')
    parser.add_argument('-p', '--prefix')
    
    args = parser.parse_args()
    #print(args)
    
    if args.command == 'qrc-add':
        qrc_path, paths = args.path[0], args.path[1:]
        qrc_add(qrc_path, paths, args.prefix, args.alias)
    elif args.command == 'ninja':
        ninja()

