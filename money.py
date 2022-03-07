#!/Users/jack/Documents/projects/22-dolla/venv/bin/python3

import sqlite3
import csv
import gspread

db = "/Users/jack/Documents/projects/22-dolla/money.db"
cat_path = "/Users/jack/Documents/projects/22-dolla/categories.csv"

def ask_for_int(message, max=1000000000):
    """
    support function to ask users for an integer
    to use in place of regular input() method
    ---
    message: string asking the user for an integer
    max: int cap on the value of the int
    returns: i, user input integer
    """
    while True:
        i = input(message)
        try:
            i = int(i)
            if i <= max:
                return i
            else:
                print("please enter and integer less than or equal to " + str(max))
        except:
            print("please enter an integer")


def pull():
    """
    move transaction values from google sheets to money.db
    ---
    returns: tuple (bool, n written / index of failed lines)
    """
    sa = gspread.service_account()
    sh = sa.open("money")
    wks = sh.worksheet("test")
    rows = wks.get_all_values()[1:] # dont include headers
    con = sqlite3.connect(db)
    cur = con.cursor()
    fail = []
    for i, r in enumerate(rows, 2):
        try:
            with con:
                cur.execute("INSERT INTO flow VALUES (NULL,?,?,?,?,?,?,?,?,?,?)",
                            (float(r[0]), # amount
                             r[1], # curency
                             int(bool(r[2])), # cc
                             int(bool(r[3])), # out
                             int(r[4]), # yyyymmdd
                             int(r[4][:4]), # yyyy
                             int(r[4][4:6]), # mm
                             int(r[4][-2:]), # dd
                             r[5], # category
                             r[6])) # notes
        except:
            fail.append(i)
    con.close()
    if len(fail) == 0:
        wks.batch_clear(["A2:G900"])
        return (True, len(rows))
    else:
        clear = []
        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        for i in range(2, 900):
            for c in cols:
                clear.append(c + str(i))
        wks.batch_clear(clear)
        return (False, fail)

def fix_cats():
    """
    lists all categories in db not in categories.csv
    asks users to switch rows from non-csv to csv categories
    """
    # get categories from csv
    cats = []
    with open(cat_path, newline='') as csvfile:
        c_rows = csv.reader(csvfile, delimiter=',')
        for r in c_rows:
            for c in r:
                if not c.startswith('#'):
                    cats.append(c)
    # get unique categories in db
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT cat FROM flow")
    db_cats = cur.fetchall()
    # compare
    wrong = []
    for c in db_cats:
        if c[0] not in cats:
            wrong.append(c[0])
    # choose swap
    for i, c in enumerate(wrong, 1):
        print(str(i) + ": " + c)
    wi = ask_for_int("index of category to fix, '0' to quit: ", len(wrong))
    if wi == 0:
        return
    for i, c in enumerate(cats, 1):
        print(str(i) + ": " + c)
    ci = ask_for_int("index of correct category, '0' to quit: ", len(cats))
    if ci == 0:
        return
    # swap
    with con:
        cur.execute("UPDATE flow SET cat = ? WHERE cat = ?",
                    (cats[ci - 1], wrong[wi - 1]))
    con.close()
    return

def main():
    "command line ui"
    functions = (pull, fix_cats)
    for i, f in enumerate(functions, 1):
        print(str(i) + ": " + f.__name__)
    sel = ask_for_int("select function index, enter '0' to quit: ", len(functions))
    if sel == 0:
        return
    else:
        f = functions[sel - 1]()
        if type(f) == list or type(f) == tuple:
            for r in f:
                print(r)
        else:
            print(f)
        return

if __name__ == "__main__":
    main()

