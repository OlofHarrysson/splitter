from lxml import etree


def save_xml(element, outfile):
  element.write(outfile)
  clean_up_xml(outfile)


def print_xml(root, only_keys=False):
  for child in root.iter():
    if only_keys:
      print(child.tag)
    else:
      print(child.tag, child.attrib)


def clean_up_xml(xml_file):
  parser = etree.XMLParser(remove_blank_text=True)
  root = etree.parse(xml_file, parser).getroot()
  tree = etree.ElementTree(root)
  tree.write(xml_file, encoding='utf-8', pretty_print=True)

  # TODO: Doesn't seem like this is needed?
  # prepend_info = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n\n'
  # with open(xml_file) as f:
  #   xml_data = f.read()

  # with open(xml_file, 'w') as f:
  #   f.write(prepend_info + xml_data)


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