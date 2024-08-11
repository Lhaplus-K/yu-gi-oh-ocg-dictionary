import glob
import pandas
import xml.etree.ElementTree as ET
import zipfile
from os import path
from pandas import DataFrame
from pandera import Column, DataFrameSchema, Index

READ_CSV_PATH = 'in/*.csv'
OUT_DIR = 'out/'
OUT_FILE_NAME = 'yugioh-dic'
EXT_PLIST = '.plist'
EXT_TEXT = '.txt'
EXT_ZIP = '.zip'
SUFFIX_MAC = 'mac_add'
SUFFIX_PLIST = 'mac_user'
SUFFIX_UTF8 = 'google'
SUFFIX_UTF16LE = 'microsoft'
SUFFIX_ZIP = 'gboard'
XML_HEADER = '<?xml version="1.0" encoding="utf-8"?>'
DOCTYPE = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'

def load_data_frame(filepath: str) -> DataFrame:
  schema = DataFrameSchema(
    {
      'Reading': Column(str),
      'Word': Column(str),
      'Category': Column(str, default='固有名詞')
    },
    index=Index(int),
    strict=True,
    coerce=True
  )
  df = pandas.read_csv(filepath)
  df = schema.validate(df)
  df = df.reindex(columns=['Reading', 'Word', 'Category'])
  return df

def generate():
  file_base_path = path.join(OUT_DIR, OUT_FILE_NAME)
  files = glob.glob(READ_CSV_PATH)
  df_list = []
  for file in files:
    file_df = load_data_frame(file)
    df_list.append(file_df)
  df = pandas.concat(df_list, ignore_index=True)
  df = df.drop_duplicates()
  filename_utf8 = f'{file_base_path}_{SUFFIX_UTF8}{EXT_TEXT}'
  df.to_csv(path_or_buf=filename_utf8, sep='\t', header=False, index=False, encoding='utf-8')
  with zipfile.ZipFile(file=f'{file_base_path}_{SUFFIX_ZIP}{EXT_ZIP}', mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    zf.write(filename=filename_utf8, arcname=f'{OUT_FILE_NAME}{EXT_TEXT}')
  generate_for_utf16le(df, file_base_path)
  generate_for_mac(df, file_base_path)
  generate_for_plist(df, file_base_path)

def generate_for_mac(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  df = df.replace('固有名詞', 'その他の固有名詞')
  df = df.replace('短縮よみ', 'その他の固有名詞')
  df.to_csv(path_or_buf=f'{file_base_path}_{SUFFIX_MAC}{EXT_TEXT}', sep=',', header=False, index=False, encoding='utf-8')

def generate_for_utf16le(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  df.to_csv(path_or_buf=f'{file_base_path}_{SUFFIX_UTF16LE}{EXT_TEXT}', sep='\t', header=False, index=False, encoding='utf-16')

def generate_for_plist(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  root = ET.Element('plist')
  root.set('version', '1.0')
  array_node = ET.SubElement(root, 'array')
  for row in df.itertuples():
    add_plist_node(array_node, row.Word, row.Reading)
  tree = ET.ElementTree(pretty_print(root))
  with open(f'{file_base_path}_{SUFFIX_PLIST}{EXT_PLIST}', 'wb') as file:
    file.write(f'{XML_HEADER}\n'.encode('utf8'))
    file.write(f'{DOCTYPE}\n'.encode('utf8'))
    tree.write(file, encoding='utf-8', xml_declaration=False)

def add_plist_node(parent: ET.Element, word: str, reading: str):
  dict_node = add_xml_child_node(parent, 'dict')
  add_xml_child_node(dict_node, 'key', 'phrase')
  add_xml_child_node(dict_node, 'string', word)
  add_xml_child_node(dict_node, 'key', 'shortcut')
  add_xml_child_node(dict_node, 'string', reading)

def add_xml_child_node(parent: ET.Element, tag: str, text: str=None) -> ET.Element:
  child = ET.SubElement(parent, tag)
  if text is not None:
    child.text = text
  return child

def pretty_print(current: ET.Element, parent: ET.Element=None, index: int=-1, depth: int=0) -> ET.Element:
  for i, node in enumerate(current):
    pretty_print(node, current, i, depth + 1)
  if parent is None:
    return current
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