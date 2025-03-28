import os
import xml.etree.ElementTree as ET

RULE = """
rule uic
    command = pyside6-uic $in -o $out
"""

BUILD = "build {}: uic {}\n"

def get_class(path):
    tree = ET.parse(path)
    root = tree.getroot()
    item = root.find('class')
    return item.text

def main():
    basedir = os.getcwd()
    with open(os.path.join(basedir, 'build.ninja'), 'w', encoding='utf-8') as file:
        file.write(RULE)
        for root, dirs, files in os.walk(basedir):
            for f in files:
                if os.path.splitext(f)[1] == '.ui':
                    p = os.path.join(root, f)
                    c = get_class(p)
                    src = os.path.relpath(p, basedir)
                    dst = os.path.relpath(os.path.join(root, "Ui_{}.py".format(c)))
                    file.write(BUILD.format(dst, src))

