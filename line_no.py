import pathlib
p = pathlib.Path(r'e:\perfume tracker\app.py')
for i,l in enumerate(p.read_text(encoding='utf-8').splitlines(), start=1):
    if 70<=i<=85:
        print(i, l)
