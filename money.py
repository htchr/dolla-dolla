#!/Users/jack/Documents/projects/22-dolla/venv/bin/python3

import sqlite3
import csv
import datetime
import gspread
import matplotlib.pyplot as plt

db = "/Users/jack/Documents/logs/money.db"
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

def get_cats(mode="all", groups=[]):
    """
    get a list of transaction category strings from categories.csv
    ---
    mode: string; all, in, out, groups (must have value for groups)
    groups: list of string(s) of sub category(s) to include
    returns: list of all included transaction categories
    """
    cats = []
    if mode == "all":
        groups = ["#move", "#in", "#give", "#later", "#pay", "#cola", "#spend", "#misc"]
    elif mode == "in":
        groups = ["#in"]
    elif mode == "out":
        groups = ["#give", "#later", "#pay", "#cola", "#spend", "#misc"]
    with open(cat_path, newline='') as csvfile:
        c_rows = csv.reader(csvfile, delimiter=',')
        for r in c_rows:
            if r[0] in groups:
                cats = cats + r[1:]
            else:
                continue
    return cats
 
def pull():
    """
    move transaction values from google sheets to money.db
    ---
    returns: tuple (bool, n written / index of failed lines)
    """
    sa = gspread.service_account()
    sh = sa.open("money")
    wks = sh.worksheet("flow")
    rows = wks.get_all_values()[1:] # dont include headers
    con = sqlite3.connect(db)
    cur = con.cursor()
    fail = []
    for r in rows:
        print(r)
        if r[0] == '' or r[0] == '0':
            fail.append(r)
        else:
            try:
                with con:
                    cur.execute("INSERT INTO flow VALUES (NULL,?,?,?,?,?,?,?,?,?,?)",
                                (float(r[0]), # amount
                                 str(r[1]), # curency
                                 int(bool(r[2])), # cc
                                 int(bool(r[3])), # out
                                 int(r[4]), # yyyymmdd
                                 int(r[4][:4]), # yyyy
                                 int(r[4][4:6]), # mm
                                 int(r[4][-2:]), # dd
                                 r[5], # category
                                 r[6])) # notes
            except:
                fail.append(r)
    con.close()
    wks.batch_clear(["A2:G900"])
    for i in range(len(fail)):
        fail[i] = ['0' if j == '' else j for j in fail[i]] 
        print(fail[i])
    wks.update("A2:G" + str(len(fail) + 1), fail)
    if len(fail) == 0:
        return (True, len(rows))
    else:
        return (False, len(fail))

def fix_cats():
    """
    lists all categories in db not in categories.csv
    asks users to switch rows from non-csv to csv categories
    """
    # get categories from csv
    cats = get_cats()
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

def expense_pie(years=0, months=0):
    """
    plot a pie-chart of expenses
    narrow down by year and month
    ---
    years: int
    months: int
    return: None
    """
    if not years:
        year = datetime.datetime.now().date().year
        years = [y for y in range(2022, year+1)]
    if not months:
        months = [1,2,3,4,5,6,7,8,9,10,11,12]
    years = list(years)
    months = list(months)
    out_cats = get_cats("out")
    cats = {}
    con = sqlite3.connect(db)
    cur = con.cursor()
    for y in years:
        for m in months:
            cur.execute("""SELECT * FROM flow WHERE 
                           year = ?
                           AND month = ?""",
                        (y,m))
            for r in cur.fetchall():
                if r[9] not in out_cats:
                    continue
                elif r[9] not in list(cats.keys()):
                    cats[r[9]] = 0
                    cats[r[9]] += r[1]
                else:
                    cats[r[9]] += r[1]
    con.close()
    labels = []
    total = sum(list(cats.values()))
    for c, v in zip(list(cats.keys()), list(cats.values())):
        labels.append(c + ' ' 
                      + str(round((v / total) * 100, 2)) 
                      + "%" + str(v))
    plt.pie(list(cats.values()), labels=labels)
    plt.show()

def main():
    "command line ui"
    functions = (pull, fix_cats, expense_pie)
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

