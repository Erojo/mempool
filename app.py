from flask import Flask, json, render_template, request, jsonify
import requests
import json
import sqlite3
import datetime
import collections

# Proceso para ejecutar la web app
# PARECE QUE LO SIGUIENTE NO ES NECESARIO EN VS CODE-->Indicarle a flask en el terminal que el fichero .py es una app de flask. En este caso --> $env:FLASK_APP = "app"
# Ejecutar --> flask run

# turn this file into a web app
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/getFees")
def getFees():

    # Get request
    r =  requests.get('https://mempool.space/api/v1/fees/recommended')
    # Store in database
    addFees(r.text)

    # Read fees stored in tables
    rows= readFees("SELECT fastestFee, halfHourFee, hourFee, minimumFee FROM recomm_fees ORDER BY date_inserted DESC")
    # Convert query to objects of key-value pairs
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d["fastestFee"] = row[0]
        d["halfHourFee"] = row[1]
        d["hourFee"] = row[2]
        d["minimumFee"] = row[3]
        objects_list.append(d)
    j = json.dumps(objects_list)
    # print(j)
    return j

# INSERT RECORD
def addFees(fees):

    try:
        fees = json.loads(fees)
        date_created = datetime.datetime.now()

        conn = sqlite3.connect("mempool.db", detect_types=sqlite3.PARSE_DECLTYPES)
        # Create a cursor
        c = conn.cursor()
        c.execute("INSERT INTO recomm_fees (fastestFee, halfHourFee, hourFee, minimumFee, date_inserted) VALUES (?, ?, ?, ?, ?)", (fees["fastestFee"], fees["halfHourFee"], fees["hourFee"], fees["minimumFee"], date_created))

        # Commit our command
        conn.commit()

        # Close our connection
        conn.close()
    except:
        print("Error in addFees")
    finally:
        print("End addFees")

def readFees(strSQL):

    conn = sqlite3.connect("mempool.db")

    # Create a cursor
    c = conn.cursor()

    # Query the database
    c.execute(strSQL)

    items = c.fetchall()

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

    return items