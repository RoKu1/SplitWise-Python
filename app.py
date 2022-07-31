from ast import Expr
from operator import methodcaller
from urllib import response
import sqlite3, sys, os, json, re
from flask import Flask,  Response, make_response, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)


"""
ORM Models Here
"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    def __repr__(self):
        return f'<User {self.firstname} {self.lastname}  || {self.email}>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    whopaid = db.Column(db.String(80), nullable=False)
    whoowes = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer)
    
class Split():
    def __init__(self, whopaid, whoowes, howmuch) -> None:
        self.whopaid = whopaid 
        self.whoowes = whoowes
        self.howmuch = howmuch
    
    def addExpense(self, splits : list):
        for split in splits:
            res = db.session.query(Expense).filter(Expense.whopaid == split.whopaid).filter(Expense.whoowes == split.whowes).first()
            if res :
                res.amount += split.howmuch 
                # res.update()
            res = db.session.query(Expense).filter(Expense.whopaid == split.whoowes).filter(Expense.whoowes == split.whopaid).first()
            if res:
                res.amount -= split.howmuch 
                # res.update()
            else:
                new_Exp = Expense(whopaid=split.whopaid, whoowes=split.whoowes, amount=split.howmuch)
                db.session.add(new_Exp)

            db.session.commit()

    def __str__(self) -> str:
        return f"{self.whopaid} --> {self.howmuch} -->{self.whoowes}" 

class Settle():
    def __init__(self) -> None:
        pass

    def settleExpense(self, split: Split):
        try:
            print(split)
            split.howmuch = -1 * split.howmuch
            res = db.session.query(Expense).filter(Expense.whopaid == split.whopaid).filter(Expense.whoowes == split.whoowes).first()
            if res :
                res.amount -= split.howmuch 
                # res.update()
            res = db.session.query(Expense).filter(Expense.whopaid == split.whoowes).filter(Expense.whoowes == split.whopaid).first()
            if res:
                res.amount += split.howmuch 
                # res.update()
            else:
                new_Exp = Expense(whopaid=split.whopaid, whoowes=split.whoowes, amount=split.howmuch)
                db.session.add(new_Exp)

            db.session.commit()
            return "", 200
        except sqlite3.Error as e:
            return str(e), 400


class Exp():
    def __init__(self) -> None:
        pass

    def addExpense(self, splits : list):
        for split in splits:
            print(split)
            try:
                split.howmuch = -1 * split.howmuch
                res = db.session.query(Expense).filter(Expense.whopaid == split.whopaid).filter(Expense.whoowes == split.whoowes).first()
                if res :
                    res.amount += split.howmuch 
                else:
                    res = db.session.query(Expense).filter(Expense.whopaid == split.whoowes).filter(Expense.whoowes == split.whopaid).first()
                    if res:
                        res.amount -= split.howmuch 
                    else:
                        new_Exp = Expense(whopaid=split.whopaid, whoowes=split.whoowes, amount=split.howmuch)
                        db.session.add(new_Exp)
            except sqlite3.Error as e:
                return str(e), 400

        db.session.commit()
        return "", 200

"""
Multiple persons can pay in equal class
"""

class EqualExp(Exp):
    def __init__(self) -> None:
        self.listOfSplits = [] 

    def divideSplits(self,  whopaid : list, whoowes : list, howmuch : list):
        self.listOfSplits = [] 

        howmuch = [int(x) for x in howmuch]
        totalamt = sum(howmuch)
        perUser = totalamt / len(whoowes)
        trans = [0 for x in range(len(whoowes))]
        posSum = 0
        for i in range(len(whoowes)):
            if whoowes[i] in whopaid:
                trans[i] = howmuch[i] - perUser
            else:
                trans[i] -= perUser
            if trans[i] > 0:
                posSum += trans[i]

        # print(trans)
        for i in range(len(trans)):
            if trans[i] > 0:
                for j in range(len(trans)):
                    if trans[j] < 0:
                        # print(i, j)
                        # print(whopaid[i], whoowes[j], trans[j] * (trans[i] / posSum))
                        self.listOfSplits.append(Split(whopaid[i], whoowes[j], trans[j] * (trans[i] / posSum)))
        print(self.listOfSplits)
        return super().addExpense(self.listOfSplits)

"""
Only single person can pay for exact and shares
"""
class ExactExp(Exp):
    def __init__(self) -> None:
        self.listOfSplits = [] 

    def divideSplits(self,  whopaid : str, howmuch : int, whoowes : list, amts : list) -> list:
        self.listOfSplits = [] 
        amts = [int(x) for x in amts]
        # print(amts)
        if sum(amts) != howmuch:
            return "Amounts do not match", 400
        else:
            for i in range(len(whoowes)):
                if whopaid != whoowes[i]:
                    self.listOfSplits.append(Split(whopaid, whoowes[i], -1 * amts[i]))

        # print(self.listOfSplits)
        return super().addExpense(self.listOfSplits)
        # return self.listOfSplits


class SharesExp(Exp):
    def __init__(self) -> None:
        self.listOfSplits = []
    
    def divideSplits(self, whopaid : str, howmuch: int, whoowes : list, shares : list) -> list:
        self.listOfSplits = [] 
        shares = [int(s) for s in shares]
        totalshares = sum(shares)

        for i in range(len(whoowes)):
            amt = round((howmuch / totalshares) * shares[i], 2)
            print(amt)
            self.listOfSplits.append(Split(whopaid, whoowes[i], -1 * amt ))

        # print(self.listOfSplits)
        return super().addExpense(self.listOfSplits)
        # return self.listOfSplits
        


    
"""
Routes Here
"""
@app.route('/api/v1/poll', methods=['GET'])
def poller():
    try:
        userData = {}
        json_data = json.loads(str(request.data, encoding='utf-8'))
        uid = json_data["userid"]
        res = db.session.query(Expense).filter(Expense.whopaid == uid).all()
        # print(res)
        for exp in res:
            print(exp.whopaid,exp.whoowes, exp.amount)
            userData[exp.whoowes] = exp.amount  
        res = db.session.query(Expense).filter(Expense.whoowes == uid).all()
        # print(res)
        for exp in res:
            print(exp.whopaid, exp.whoowes, exp.amount)
            userData[exp.whopaid] = -1 * exp.amount  
        # print(userData)
        if not userData:
            return "None", 200
        del userData[uid]
        return userData, 200

    except sqlite3.Error as e:
        return str(e), 400
    except Exception as e:
        return str(e), 400


@app.route('/api/v1/settle', methods=['POST'])
def settlement():
    try:
        json_data = json.loads(str(request.data, encoding='utf-8'))
        users = [json_data["whopaid"], json_data["towhom"]]
        if not checkUserPresence(users):
            return "User in expense does not exist in db", 500
        sp =  Split(json_data["whopaid"], json_data["towhom"], int(json_data["howmuch"]))
        print(sp)
        return Settle().settleExpense(split=sp)

    except sqlite3.Error as e:
        return str(e), 400
    except Exception as e:
        return str(e), 400
     

def checkUserPresence(l2) -> bool:
    try:
        userNames = [user.email for user in User.query.all()]
        for u in l2:
            if u not in userNames:
                return False
        
        return True    
    except sqlite3.Error as e:
        return str(e), 400
    except Exception as e:
        return str(e), 400


@app.route('/api/v1/expense', methods=['POST'])
def expense_end():
    try:
        json_data = json.loads(str(request.data, encoding='utf-8'))
        print(json_data)
        if not checkUserPresence(json_data["whoowes"]):
            return "User in expense does not exist in db", 500
        if json_data["type"] == "EQUAL":
            return EqualExp().divideSplits(whopaid=json_data["whopaid"], whoowes=json_data["whoowes"], howmuch=json_data["howmuch"])
        elif json_data["type"] == "EXACT":
            return ExactExp().divideSplits(whopaid=json_data["whopaid"], whoowes=json_data["whoowes"], howmuch=int(json_data["howmuch"]), amts=json_data["amounts"])
        elif json_data["type"] == "SHARES":
            return SharesExp().divideSplits(whopaid=json_data["whopaid"], whoowes=json_data["whoowes"], howmuch=int(json_data["howmuch"]), shares=json_data["shares"])
        else:
            return "Not expected data", 400

    except sqlite3.Error as e:
        return str(e), 400

    except Exception as e:
        return str(e), 400


@app.route('/api/v1/users/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_endpoint():
    try:
        json_data = json.loads(str(request.data, encoding='utf-8'))
        # c = conn.cursor()
        if request.method == 'GET':
            try:
                user = User.query.get(json_data["userid"])
                if not user:
                    return "User not found ", 404
                return str(user) , 200
            except Exception as e:
                return "FAILURE TO GET USER", 400

        elif request.method == 'POST':
            print("POST<<<", json_data)
            try:
                new_User = User(firstname=json_data["fname"], lastname=json_data["lname"], email=json_data["email"])
                db.session.add(new_User)
                db.session.commit()
                return str(new_User.id), 201
            
            except sqlite3.Error as e:
                return str(e)

            except Exception as e:
                return str(e)

        elif request.method == 'PUT':
            print("PUT<<<", json_data)
            try:
                db.session.query(User).filter(User.email == json_data["email"]).update({"firstname":json_data["fname"], "lastname":json_data["lname"]}, synchronize_session="fetch")
                db.session.commit()
                return "", 200
            
            except sqlite3.Error as e:
                return str(e)

            except Exception as e:
                return str(e)
        
        elif request.method == 'DELETE':
            try:
                print("DELETE<<<", json_data)
                user = User.query.get(json_data["userid"])
                if not user:
                    return "User not found ", 404

                db.session.delete(user)
                db.session.commit()
                # uid = json_data["userid"]
                # query = "DELETE FROM users WHERE userid = '{}';".format(uid)
                # c.execute(query)
                # conn.commit()
                return "", 202
            except sqlite3.Error as e:
                return str(e)

            except Exception as e:
                return str(e)
  
    except sqlite3.Error as e:
        return str(e)
    except Exception as e:
        return str(e), 400


if __name__ == "__main__":
    try:
        with app.app_context():
            db.create_all()
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=True, host='0.0.0.0', port=port)

    
    except Exception as e:
        print(e)
        sys.exit(1)