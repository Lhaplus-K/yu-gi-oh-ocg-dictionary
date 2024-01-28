import pandas
import zipfile
from os import path

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

if __name__ == '__main__':
  generate()