import sqlite3
from tabulate import tabulate
from datetime import datetime
conn=sqlite3.connect("portfolio.db")
c=conn.cursor()
c.execute("PRAGMA FOREIGN_KEYS = ON;")

c.execute("""CREATE TABLE IF NOT EXISTS USER(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERNAME TEXT UNIQUE,
                PASSWORD TEXT 
);
""")

c.execute("""CREATE TABLE IF NOT EXISTS INVESTMENTS(
                INVEST_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID INTEGER,
                ASSET_NAME TEXT,
                ASSET_TYPE TEXT,
                SHARES REAL,
                BUY_PRICE REAL,
                CURRENT_PRICE REAL,
                INVESTED_AMOUNT REAL,
                AVERAGE_PRICE REAL,
                TOTAL_RETURN REAL,
                INVESTED_DATE TEXT,
                FOREIGN KEY (USER_ID) REFERENCES USER (ID) ON DELETE CASCADE
);
""")
conn.commit()
conn.close()

def register():
    print("\n REGISTER NEW USER ")
    username=input("ENTER THE USERNAME :").upper()
    password=input("ENTER THE 4 DIGIT PASSWORD :")
    if not password.isdigit():
        print("THE PASSWORD SHOULD BE OF 4 DIGITS ")
        return
    confirm=input(" CONFIRM PASSWORD : ")
    if password != confirm:
        print("PASSWORD DOES NOT MATCH")
        return
    conn=sqlite3.connect("portfolio.db")
    c=conn.cursor()
    try:
        c.execute("INSERT INTO USER (username,password) VALUES (?,?)",(username,password))
        conn.commit()
    except sqlite3.IntegrityError:
            print(" USERNAME ALREADY EXISTS. PLEASE TRY ANOTHER ")
    else:
        print("REGISTERED SUCCESSFULLY")
    conn.close()


def login():
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    print("\n LOGIN HERE ")
    username = input("USERNAME :").upper()
    password = input("PASSWORD :")
    c.execute("SELECT ID FROM USER WHERE username= ? AND password = ? ",(username,password) )
    user=c.fetchone()
    conn.close()
    if user:
        print("LOGIN SUCCESSFUL ")
        return user[0]
    else:
        print("INVALID CREDENTIALS")
        return  None

def add_investment(login_user_id):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    print("\nADD INVESTMENT")
    user_id=login_user_id
    asset_name=input("ENTER THE ASSET NAME :").upper()
    asset_type=input("ENTER THE ASSET TYPE (STOCK/ETF/MF/GOLD/CRYPTO) :").upper()
    shares=float(input("ENTER THE QUANTITY OF SHARES/UNITS :"))
    buy_price=float(input("ENTER THE BUY PRICE OR NAV :"))
    invested_date=datetime.now().strftime("%d-%m-%Y")
    c.execute("SELECT shares,average_price,invested_amount "
              "FROM INVESTMENTS WHERE user_id= ? AND asset_name=?",
              (user_id, asset_name))
    inexistance=c.fetchone()
    if inexistance:
        old_shares, old_average_price, old_invested_amount= inexistance
        current_invested_amount=(shares*buy_price)+old_invested_amount
        current_shares = old_shares+shares
        current_average_price=current_invested_amount/current_shares
        c.execute("""
                    UPDATE INVESTMENTS
                    SET shares=?,invested_amount=?,average_price=?,buy_price=?,current_price=?,invested_date=?
                    WHERE user_id=? AND asset_name=?
                """, (current_shares, current_invested_amount, current_average_price,buy_price,buy_price,
                      invested_date,user_id, asset_name))
        print("\nTHE CURRENT ASSET DATA IS UPDATED ")
    else:
        invested_amount= buy_price * shares
        average_price=buy_price
        current_price = buy_price
        total_return=0
        c.execute("INSERT INTO INVESTMENTS(user_id,asset_name,asset_type,shares,buy_price,current_price,"
              "invested_amount,average_price,total_return,invested_date) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (user_id,asset_name,asset_type,shares,buy_price,current_price,invested_amount,
                average_price,total_return,invested_date))
    conn.commit()
    conn.close()
    print("INVESTMENT ADDED SUCCESSFULLY ")

def update_investment(user_id):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    print("\nUPDATE INVESTMENT")
    asset_name=input("ENTER THE ASSET NAME TO BE UPDATED :").upper()
    c.execute("SELECT shares,average_price,invested_amount,current_price "
              "FROM INVESTMENTS WHERE user_id= ? AND asset_name=?",
              (user_id,asset_name))
    holdings=c.fetchone()

    if holdings :
        old_shares,old_average_price,old_invested_amount,current_price=holdings
        print("\nNUMBER OF OLD SHARES :",old_shares)
        print("\nPREVIOUS BUYING PRICE :",old_average_price)
        print("\nPREVIOUS INVESTED AMOUNT :",old_invested_amount)

        current_shares=float(input("ENTER THE NUMBER OF SHARES NEWLY BOUGHT : "))
        current_buy_price=float(input("ENTER THE NEW BUYING PRICE :"))
        total_shares=(old_shares+current_shares)
        total_invested_amount=(current_shares*current_buy_price)+(old_average_price*old_shares)
        average_price=(total_invested_amount/total_shares)
        total_return=(current_buy_price-average_price)*total_shares
        invested_date = datetime.now().strftime("%d-%m-%Y")

        c.execute("""
            UPDATE INVESTMENTS
            SET shares=?,invested_amount=?,average_price=?,buy_price=?,current_price=?,total_return=?,invested_date=?
            WHERE user_id=? AND asset_name=?
        """, (total_shares, total_invested_amount,average_price,current_buy_price,
             current_buy_price,total_return,invested_date,user_id, asset_name))
        conn.commit()
        print("\nUPDATED INVESTMENT PORTFOLIO ")
        print(" AVERAGE PRICE: ",average_price)
    else:
        print("INVALID DETAILS")

    conn.close()

def update_market(user_id):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    print("\nUPDATED MARKET PRICES")
    asset_name=(input("ENTER THE ASSET NAME TO BE UPDATED :")).upper()
    new_current_price=float(input("ENTER THE LIVE MARKET PRICE :"))
    c.execute("SELECT shares,buy_price,average_price,total_return "
              "FROM INVESTMENTS WHERE user_id= ? AND asset_name=?",
              (user_id, asset_name))
    market=c.fetchone()
    if market:
        shares,buy_price,average_price,total_return=market
        total_return = (new_current_price-average_price)*shares
        invested_date = datetime.now().strftime("%d-%m-%Y")
        c.execute("""
                    UPDATE INVESTMENTS
                    SET current_price=?, total_return=?,invested_date=?
                    WHERE user_id=? AND asset_name=?
                """, (new_current_price,total_return,invested_date,user_id, asset_name))
        conn.commit()
        print("\n LIVE MARKET PRICE OF " +asset_name+ " IS NOW AT " +str(new_current_price))
        print(" TOTAL RETURN ON INVESTMENT : "+str(total_return))
    else:
        print("\n NO ASSET DATA AVAILABLE FOR THIS USER")

    conn.close()

def view_portfolio(user_id):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    print("\nYOUR PORTFOLIO ")
    c.execute("""
        SELECT asset_name, asset_type, shares, average_price, current_price, invested_amount, total_return
        FROM INVESTMENTS
        WHERE user_id=?
    """, (user_id,))

    rows = c.fetchall()

    total_invested_amount = 0
    total_current_value = 0
    total_pnl=0

    if not rows:
        print(" NO DATA FOUND ")
        conn.close()
        return
    table_data=[]
    for row in rows:
            (asset_name, asset_type, shares, average_price, current_price,
             invested_amount, total_return) = row
            shares = float(shares)
            average_price = float(average_price)
            current_price = float(current_price)
            invested_amount = float(invested_amount)
            current_value = shares * current_price
            pnl = current_value - invested_amount

            total_invested_amount += invested_amount
            total_current_value += current_value
            table_data.append([asset_name,asset_type,shares,average_price,current_price,invested_amount,current_value,pnl])

    print(" \nPORTFOLIO IN DETAILED")
    total_pnl = total_current_value - total_invested_amount
    columns=len(table_data[0])
    table_data.append(["-"*10 for _ in range(columns)])
    table_data.append(["TOTAL","--","--","--","--",total_invested_amount,total_current_value,total_pnl])
    print(tabulate(table_data,headers=["ASSET","TYPE","SHARES","AVERAGE","CURRENT PRICE","INVESTED","CURRENT VALUE","PnL"]))
    conn.close()

def sell_shares(user_id):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()

    print( " \nSELL SHARES ")
    asset_name = input("Enter Asset Name you want to sell: ").upper()

    c.execute("""
        SELECT shares, average_price, current_price, invested_amount, total_return
        FROM INVESTMENTS WHERE user_id=? AND asset_name=?
    """, (user_id, asset_name))
    row = c.fetchone()

    if not row:
        print("\n No such asset in your portfolio.")
        conn.close()
        return

    shares = float(row[0])
    avg_price = float(row[1])
    current_price = float(row[2])
    invested_amount = float(row[3])
    total_return = float(row[4])

    print("\nAvailable Shares: ",shares)
    sell_qty = float(input("Enter number of shares you want to sell: "))

    if sell_qty > shares:
        print("\n You cannot sell more shares than you have ")
        conn.close()
        return

    sell_value = sell_qty * current_price
    new_shares = shares - sell_qty
    new_invested_amount = avg_price * new_shares
    new_current_value = new_shares * current_price
    new_total_return = new_current_value - new_invested_amount

    if new_shares == 0:
        c.execute("DELETE FROM INVESTMENTS WHERE user_id=? AND asset_name=?", (user_id, asset_name))
        print("\n All shares sold. Asset removed from portfolio database.")
    else:
        c.execute("""
            UPDATE INVESTMENTS
            SET shares=?, invested_amount=?, average_price=?, total_return=?, current_price=?
            WHERE user_id=? AND asset_name=?
        """, (new_shares, new_invested_amount,avg_price, new_total_return, current_price, user_id, asset_name))

        print("\n Sold :",sell_qty ,"\n shares of :",asset_name )
        print("Remaining Shares: ",new_shares)
        print("Updated Invested Amount: ",new_invested_amount)
        print("New pnl: ",new_total_return)

    conn.commit()
    conn.close()

while True:
    print(" PORTFOLIO DETAILS ")
    print("1. REGISTER ")
    print("2. LOGIN ")
    print("3. EXIT ")
    choice = input(" ENTER THE CHOICE :")
    if choice== '1':
        register()
    elif choice=='2':
        user_id = login()
        if user_id:
            while True:
                print(" \nMAIN MENU ")
                print("1. ADD INVESTMENT")
                print("2. UPDATE INVESTMENT")
                print("3. UPDATE MARKET PRICE")
                print("4. VIEW INVESTMENT ")
                print("5. EXIT INVESTMENT ")
                print("6. LOGOUT ")
                user_choice= input("ENTER THE CHOICE FOR INVESTMENT :")
                if user_choice=='1':
                    add_investment(user_id)
                elif user_choice=='2':
                    update_investment(user_id)
                elif user_choice=='3':
                    update_market(user_id)
                elif user_choice=='4':
                    view_portfolio(user_id)
                elif user_choice=='5':
                    sell_shares(user_id)
                elif user_choice=='6':
                    print("\nLOGOUT")
                    break
                else:
                    print("INVALID CHOICE BY USER")
    elif choice=='3':
        print("YOU HAVE EXIT FROM THE PORTFOLIO ")
        break
    else:
        print("INVALID CHOICE.SORRY")







#
# # register()
# user_id=login()
# # add_investment()
# if user_id:
#     add_investment(user_id)
#     update_investment(user_id)
# # if user_id:
#   # update_market(user_id)
# # if user_id:
#     # sell_shares(user_id)


