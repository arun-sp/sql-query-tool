from flask import Flask, redirect, url_for, render_template, request, session
import pymysql
import psycopg2

app = Flask(__name__)
app.secret_key = "someSecretKey"


def sqlConnect (db, host, port, user, pw, dbname):

    if (db == 1):
        connection = pymysql.connect(host=host, port=int(port), user=user, passwd=pw, db=dbname)
    elif (db == 2):
        connection = psycopg2.connect(host=host, port=int(port), user=user, password=pw, dbname=dbname)

    return connection

@app.route("/", methods=["POST", "GET"])
def homepage():

    if request.method == 'POST':

        if request.form["form"] =="connect":

            session["db"] = int(request.form["db"])
            session["host"] = request.form["host"]
            session["port"] = request.form["port"]
            session["user"] = request.form["user"]
            session["pw"] = request.form["pw"]
            session["dbname"] = request.form["dbname"]
            
            try:
                connection = sqlConnect(db = session["db"], host = session["host"], port = session["port"], 
                                        user = session["user"], pw = session["pw"], dbname = session["dbname"])
            except Exception as excep:
                return render_template("index.html", status= "Connection unsuccessful. 😕\nError Found: " + str(excep), 
                                        db = session["db"], host = session["host"], port = session["port"], 
                                        user = session["user"], pw = session["pw"], dbname = session["dbname"])

            return render_template("index.html", status="Connection Successful. Start querying. 😀", 
                                    db = session["db"], host = session["host"], port = session["port"],
                                    user = session["user"], pw = session["pw"], dbname = session["dbname"])
        
        elif request.form["form"] == "query":
                
            query = request.form["query"]
            connection = sqlConnect(db = session["db"], host = session["host"], port = session["port"], 
                                        user = session["user"], pw = session["pw"], dbname = session["dbname"])
            
            try:
                cursor = connection.cursor()
                cursor.execute(query)    
                connection.commit()

            except Exception as excep:    
                return render_template("index.html", status = "Query Unsuccessful. 😕\nError found: " + str(excep),
                                        db = session["db"], host = session["host"], port = session["port"],
                                        user = session["user"], pw = session["pw"], dbname = session["dbname"], query = query)                    

            if session["db"] == 1:
                
                result = cursor.fetchall()
                headers = cursor.description
                
                if headers == None:
                    return render_template("index.html", status = "Query executed successfully 😀",
                                            db = session["db"], host = session["host"], port = session["port"],
                                            user = session["user"], pw = session["pw"], dbname = session["dbname"], query = query)
                else:
                    headers = [i[0] for i in headers]
                
                return render_template("index.html", headers = headers, result = result,
                                        db = session["db"], host = session["host"], port = session["port"],
                                        user = session["user"], pw = session["pw"], dbname = session["dbname"], query = query)

            elif session["db"] == 2:

                try:
                    result = cursor.fetchall()
                    headers = [i.name for i in cursor.description]
                except Exception as excep:
                    return render_template("index.html", status = "Query executed successfully 😀",
                                            db = session["db"], host = session["host"], port = session["port"],
                                            user = session["user"], pw = session["pw"], dbname = session["dbname"], query = query)
                
                return render_template("index.html", headers = headers, result = result,
                                        db = session["db"], host = session["host"], port = session["port"],
                                        user = session["user"], pw = session["pw"], dbname = session["dbname"], query = query)

    else:
        return render_template("index.html", inp_value = "Make Connection & Start Querying")
        
if __name__=="__main__":
    app.run()