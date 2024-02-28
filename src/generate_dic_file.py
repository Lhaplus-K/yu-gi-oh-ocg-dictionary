import pandas
import xml.etree.ElementTree as ET
import zipfile
from os import path
from pandas import DataFrame

READ_CSV_PATH = 'in/yugioh-dic.csv'
OUT_DIR = 'out/'
OUT_FILE_NAME = 'yugioh-dic'
EXT_PLIST = '.plist'
EXT_TEXT = '.txt'
EXT_ZIP = '.zip'
XML = '<?xml version="1.0" encoding="utf-8"?>'
DOCTYPE = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'

def generate():
  file_base_path = path.join(OUT_DIR, OUT_FILE_NAME)
  df = pandas.read_csv(READ_CSV_PATH)
  df.to_csv(path_or_buf=f'{file_base_path}{EXT_TEXT}', sep='\t', header=False, index=False, encoding='utf-8')
  with zipfile.ZipFile(file=f'{file_base_path}{EXT_ZIP}', mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    zf.write(filename=f'{file_base_path}{EXT_TEXT}', arcname=f'{OUT_FILE_NAME}{EXT_TEXT}')
  generate_for_utf16le(df, file_base_path)
  generate_for_mac(df, file_base_path)
  generate_for_plist(df, file_base_path)

def generate_for_mac(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  df = df.replace('固有名詞', 'その他の固有名詞')
  df = df.replace('短縮よみ', 'その他の固有名詞')
  df.to_csv(path_or_buf=f'{file_base_path}_mac{EXT_TEXT}', sep=',', header=False, index=False, encoding='utf-8')

def generate_for_utf16le(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  df.to_csv(path_or_buf=f'{file_base_path}_utf16le{EXT_TEXT}', sep='\t', header=False, index=False, encoding='utf-16')

def generate_for_plist(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  root = ET.Element('plist')
  root.set('version', '1.0')
  array_node = ET.SubElement(root, 'array')
  for row in df.itertuples():
    add_plist_node(array_node, row.Word, row.Reading)
  pretty_print(root)
  tree = ET.ElementTree(root)
  with open(f'{file_base_path}_mac{EXT_PLIST}', 'wb') as file:
    file.write(f'{XML}\n'.encode('utf8'))
    file.write(f'{DOCTYPE}\n'.encode('utf8'))
    tree.write(file, encoding='utf-8', xml_declaration=False)

def add_plist_node(parent: ET.Element, word: str, reading: str):
  dict_node = add_xml_child_node(parent, 'dict')
  add_xml_child_node(dict_node, 'key', 'phrase')
  add_xml_child_node(dict_node, 'string', word)
  add_xml_child_node(dict_node, 'key', 'shortcut')
  add_xml_child_node(dict_node, 'string', reading)
  return dict_node

def add_xml_child_node(parent: ET.Element, tag: str, text: str = None):
  child = ET.SubElement(parent, tag)
  if text is not None:
    child.text = text
  return child

def pretty_print(current: ET.Element, parent: ET.Element = None, index: int = -1, depth: int = 0):
  for i, node in enumerate(current):
    pretty_print(node, current, i, depth + 1)
  if parent is None:
    return
  if index == 0:
    indent = "\t" * depth
    parent.text = f'\n{indent}'
  else:
    indent = "\t" * depth
    parent[index - 1].tail = f'\n{indent}'
  if index == len(parent) - 1:
    indent = "\t" * (depth - 1)
    current.tail = f'\n{indent}'
  return current

if __name__ == '__main__':
  generate()