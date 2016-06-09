import zipfile
import httpio

url = "http://www.elegantthemes.com/icons/elegant_font.zip"
with httpio.open(url) as fp:
    zf = zipfile.ZipFile(fp)
    print(zf.namelist())