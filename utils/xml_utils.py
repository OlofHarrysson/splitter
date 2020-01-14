from lxml import etree


def read_xml(path):
  tree = etree.parse(str(path))
  root = tree.getroot()
  return tree, root


def save_xml(element, outfile):
  element.write(outfile)
  clean_up_xml(outfile)


def clean_up_xml(xml_file):
  parser = etree.XMLParser(remove_blank_text=True)
  root = etree.parse(xml_file, parser).getroot()
  tree = etree.ElementTree(root)
  tree.write(xml_file, encoding='utf-8', pretty_print=True)


def create_element(name, attributes=None):
  if attributes == None:
    attributes = {}

  ele = etree.Element(name)
  for k, v in attributes.items():
    ele.set(k, v)

  return ele


def add_children(parent, children):
  [parent.append(c) for c in children]
  return parent