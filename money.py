#!/Users/jack/Documents/projects/22-dolla/venv/bin/python3

import gspread

sa = gspread.service_account()
sh = sa.open("money")
wks = sh.worksheet("flow")
print(wks.get_all_values())
