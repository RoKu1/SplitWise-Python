# SPLITWISE CLONE
## How To Start
    **Prequisites**
        docker desktop (on windows)(docker engine on centos)
        build the image with "docker build -t assign"
        run the image on windows with "docker run -d -p 5000:5000 --name=assign -v %cd%:/app assign"
        run the image on linux with "docker run -d -p 5000:5000 --name=assign -v $(pwd):/app assign"
        

## Features Provided
        a> be able to add users. (create)
        c> user is able to add expense(either in group or individuallu).
            i>  types of expenses: EQUAL, EXACT, SHARES
                a> EQUAL    --> equally divide share
                            --> can specify who paid(multiple users allowed)
                b> EXACT    --> can specify who owes how much
                            --> can specify single user who paid for the expense
                c> SHARES   --> can specify who owes how much share in expense
                            --> can specify single user who paid for the expense
        d> user ie able to see the balance sheet 
            --> to see what he owes and is owed (poll)
        e> user should be abel to settle any expense(bal).
            --> settle api
        ** can be done -- simplify expenses
        ** can be done -- payment capability


## Database Schemas
    **USER TABLE**
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        firstname = db.Column(db.String(100), nullable=False)
        lastname = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(80), unique=True, nullable=False)
    **EXPENSE TABLE**
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        whopaid = db.Column(db.String(80), nullable=False)
        whoowes = db.Column(db.String(80), nullable=False)
        amount = db.Column(db.Integer)



## ENDPOINTS[In Postman Collection] DESCRIPTION
    /users :-->
            get: /api/v1/user [get existing user]
                body : json of userid to get {id-->id} {body example in postman}
                resp: json of user object
            post : /api/v1/user [create new user]
                body : json of user object {uniques, id--> email, id} {body example in postman}
                resp : 201 --> if created or else other
                        200 --> if already present
            put : /api/v1/user [updating user]
                body : json of user object {uniques, id--> email, id} {body example in postman}
                resp : 200 --> if created or else other
            del : /api/v1/user
                body :  json of userid to delete {id-->id} {body example in postman}
                resp :   202: deleted 
                        404: not found
    /expense :-> 
                post: /api/v1/expense [post a expense][examples included in postman collection]
                    {
                        "userid" : "u1",
                        "whopaid" : ["u1"],
                        "howmuch" : ["100"],
                        "users" : ["u1", "u2", "u3"],
                        "type" : "shares" 
                        "amts" : "["1", "2", "2"]"
                    }
                resp:
                    {200:ok}

    /poll :->
            get: /api/v1/poll
            body:   {
                        "userid" : "u1@gmail.com"
                    }

    /settle :->
            post: /api/v1/settle
            body:   {
                    "whopaid" : "u2@gmail.com",
                        "howmuch" : "300", 
                        "towhom" : "u1@gmail.com"
                    }

### ALready Present Users
   ```
      {
         "email": "u1@gmail.com", 
         "fname": "u1fn",
         "lname":"u1ln"}
      {
        "email": "u2@gmail.com", 
        "fname": "u2fn",
        "lname":"u2ln"}
      {
        "email": "u3@gmail.com", 
        "fname": "u3fn",
        "lname":"u3ln"}
      {
        "email": "u4@gmail.com", 
        "fname": "u4fn",
        "lname":"u4ln"} ```


### Already Present Expense**
    ***None**


