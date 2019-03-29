from mobiparse import Mobi
import re

mobi = Mobi('test/b.mobi')
html,images = mobi.parse()
index = open("./output/index.html", 'w')
pattern = re.compile(r'<img alt="Missing image file".*\/>')
print pattern.findall(html)
