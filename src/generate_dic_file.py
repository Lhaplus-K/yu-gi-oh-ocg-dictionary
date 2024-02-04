import pandas
import zipfile
from os import path
from pandas import DataFrame

READ_CSV_PATH = 'in/yugioh-dic.csv'
OUT_DIR = 'out/'
OUT_FILE_NAME = 'yugioh-dic'
EXT_TEXT = '.txt'
EXT_ZIP = '.zip'

def generate():
  file_base_path = path.join(OUT_DIR, OUT_FILE_NAME)
  df = pandas.read_csv(READ_CSV_PATH)
  df.to_csv(path_or_buf=f'{file_base_path}{EXT_TEXT}', sep='\t', header=False, index=False, encoding='utf-8')
  with zipfile.ZipFile(file=f'{file_base_path}{EXT_ZIP}', mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    zf.write(filename=f'{file_base_path}{EXT_TEXT}', arcname=f'{OUT_FILE_NAME}{EXT_TEXT}')
  generate_for_utf16le(df, file_base_path)
  generate_for_mac(df, file_base_path)

def generate_for_mac(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  df = df.replace('固有名詞', 'その他の固有名詞')
  df = df.replace('短縮よみ', 'その他の固有名詞')
  df.to_csv(path_or_buf=f'{file_base_path}_mac{EXT_TEXT}', sep=',', header=False, index=False, encoding='utf-8')

def generate_for_utf16le(data_frame: DataFrame, file_base_path: str):
  df = data_frame
  df.to_csv(path_or_buf=f'{file_base_path}_utf16le{EXT_TEXT}', sep='\t', header=False, index=False, encoding='utf-16')

if __name__ == '__main__':
  generate()