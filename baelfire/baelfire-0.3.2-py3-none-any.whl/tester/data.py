from baelfire.filedict import FileDict

data = FileDict('x.yaml')
try:
    data.load()
except FileNotFoundError:
    pass
data.ensure_key_exists('me', 'This is description')
data.save()
print(data)
