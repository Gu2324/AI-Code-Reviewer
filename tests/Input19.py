import re
# Meant to match 'color' or 'colour'
if re.match('colou?r', 'color'):
    print("Match")