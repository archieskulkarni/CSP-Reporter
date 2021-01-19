import flask
from flask import request, jsonify, render_template
import sqlite3
import random
import tldextract

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>API to update and fetch CSP Reports</h1>
<p>A basic version of the api. We'll get to the document later.</p>'''


@app.route('/api/v1/cspreports/fetch', methods=['GET'])
def fetchCSP():
    conn = sqlite3.connect('cspreports.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_csp = cur.execute('SELECT * FROM cspdata;').fetchall()

    return jsonify(all_csp)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/api/v1/cspreports/update', methods=['POST'])
def postCSP():
    username = 'user' + str(random.randint(1, 1000))
    jsondata = request.get_json()
    cspValues = jsondata['csp-report']
    uri = ''
    for val in cspValues:
        if val == 'document-uri':
            uri = cspValues[val]
            break
    ext = tldextract.extract(uri)
    tld = str(ext.subdomain) + str(ext.domain) + "." + str(ext.suffix)
    data = (username, tld, str(jsondata))

    query = "INSERT INTO cspdata (userid, domain, jsondata) VALUES (?, ?, ?);"

    conn = sqlite3.connect('cspreports.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, data).fetchall()
    cur.execute('COMMIT;')
    return jsonify(results)

@app.route('/viewreports', methods=['GET'])
def viewReports():
    userid = request.args.get('user')
    query = "SELECT * FROM cspdata WHERE userid = ?"
    conn = sqlite3.connect('cspreports.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, (userid,)).fetchall()
    # content = (results))
    print(results)
    return render_template("viewreports.html", content=results, userid=userid)

app.run()