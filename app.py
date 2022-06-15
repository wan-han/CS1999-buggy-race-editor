from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql
import urllib.request

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

def tooLong():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    return cur.fetchone();

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------

@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        record = tooLong()
        return render_template("buggy-form.html", buggy = record)
    elif request.method == 'POST':
        msg=""
        qty_wheels = request.form['qty_wheels']
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        type_armor = request.form['type_armor']
        type_tyre = request.form['type_tyre']
        attack_type = request.form['attack_type']
        number_tyres = request.form['number_tyres']

        if not qty_wheels.isdigit():
            msg = f"Entered item is not a numerical value {qty_wheels}"
            return render_template("updated.html", msg = msg)

        if flag_color == flag_color_secondary:
            msg = f"Primary and secondary colour cannot be the same. "
            return render_template("updated.html", msg = msg)

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, type_armor=?, type_tyre=?, attack_type=?, number_tyres=? WHERE id=?",
                    (qty_wheels, flag_color, flag_color_secondary, flag_pattern, type_armor, type_tyre, attack_type, number_tyres, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved"

        except:
            con.rollback()
            msg = "error in update operation"

        finally:
            con.close()
            
        return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/delete/<buggy_id>')
def delete_buggy(buggy_id):
    try:
        with sql.connect(DATABASE_FILE) as con:
            cur= con.cursor()
            cur.execute(
                "DELETE FROM buggies WHERE id=?", (buggy_id,)
            )
            con.commit()
            msg = "Record successfully saved"
    except:
        con.rollback()
        msg = "error in update operation"
    finally:
        con.close()
        return render_template("updated.html", msg = msg)
        
@app.route('/buggy')
def show_buggies():
    record = tooLong()
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------

@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

@app.route('/poster')
def poster():
    return render_template("poster.html")

@app.route('/info')
def info():
    req = urllib.request.Request('https://rhul.buggyrace.net/specs/data/types.json')
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
    return render_template("info.html")

@app.route('/buggy-form')
def buggyform_show():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------

@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ['CS1999_PORT']
    app.run(debug=True, host="0.0.0.0", port=alloc_port)
