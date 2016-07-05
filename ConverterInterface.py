from flask import Flask, render_template, request, redirect, url_for, Response, flash, Markup, jsonify
from werkzeug import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
from PointlessConverter import *

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['las'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set session secret key
app.secret_key = 'some_secret'

@app.route('/')
def main():
 	return render_template('ConverterLogin.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/ConvertLas/', methods=['POST'])
def convertData():
    if request.method == 'POST':
    	filename = ""
        file = request.files['InputFile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

	dbms_name = request.form['InputDBMSname']
	user = request.form['InputUsername']
	password = request.form['InputPassword']
	maximumLevels = int(request.form['InputDepth'])
	if (user == "" and password == ""):
		Pointless(os.path.join(app.config['UPLOAD_FOLDER'], filename), "1", dbms_name, maximumLevels)
	elif (user == "" and password != ""):
		Pointless(os.path.join(app.config['UPLOAD_FOLDER'], filename), "1", dbms_name, maximumLevels, "postgres", password)
	elif (user != "" and password == ""):
		Pointless(os.path.join(app.config['UPLOAD_FOLDER'], filename), "1", dbms_name, maximumLevels, user)
	elif (user != "" and password != ""):
		Pointless(os.path.join(app.config['UPLOAD_FOLDER'], filename), "1", dbms_name, maximumLevels, user, password)
	return render_template('Viewer.html')

@app.route('/_call_empty_db', methods=['POST'])
def call_empty_db():
    count = float(request.data[1:])
    if request.data[0] == 'x':
        sql = "select * from emptyspace as es where CAST(es.x AS float) >= {0} and CAST(es.x AS float) < {1};".format( str(count), str(count + 5))
    elif request.data[0] == 'y':
        sql = "select * from emptyspace as es where CAST(es.y AS float) >= {0} and CAST(es.y AS float) < {1};".format( str(count), str(count + 5))
    elif request.data[0] == 'z':
        sql = "select * from emptyspace as es where CAST(es.z AS float) >= {0} and CAST(es.z AS float) < {1};".format( str(count), str(count + 5))
    else:
        sql = "select * from emptyspace limit 10000;"
    # sql = 'select * from emptyspace;' CAST(coalesce(<column>, '0') AS integer)
    # print sql
    result = db.engine.execute(sql)
    emptyspace = []
    for row in result:
        emptyspace.append([int(row[1]),int(row[2]),int(row[3]),int(row[4])]) # for loading empty leaf nodes
    return jsonify(result=emptyspace)

@app.route('/_call_points_db', methods=['POST'])
def call_points_db():
    count = float(request.data[1:])
    if request.data[0] == 'x':
        sql = "select x, y, z from pointcloud as pc where CAST(pc.x AS float) >= {0} and CAST(pc.x AS float) < {1};".format(str(count), str(count + 5))
    elif request.data[0] == 'y':
        sql = "select x, y, z from pointcloud as pc where CAST(pc.y AS float) >= {0} and CAST(pc.y AS float) < {1};".format(str(count), str(count + 5))
    elif request.data[0] == 'z':
        sql = "select x, y, z from pointcloud as pc where CAST(pc.z AS float) >= {0} and CAST(pc.z AS float) < {1};".format(str(count), str(count + 5))
    else:
        sql = "select x, y, z from pointcloud limit 10000;"
    # sql = 'select x, y, z from pointcloud;'
    # print sql
    result = db.engine.execute(sql)
    points = []
    for row in result:
        points.append([float(row[0]),float(row[1]),float(row[2])]) # for loading point cloud
    return jsonify(result=points)

@app.route('/_get_path', methods=['POST'])
def getPath():
    global user
    global password
    global dbms_name

    print "request path"
    coords = request.data.split(' ')
    print coords
    start, goal = coords[0], coords[1]
    nodes = get_nodes(dbms_name, user, password)
    came_from, cost_so_far =  a_star_search(nodes_dict(nodes), start, goal, nodes)
    path = reconstruct_path(came_from, goal, cost_so_far, nodes)
    print path

    return jsonify(result=path)

@app.route('/_get_points', methods=['GET'])
def getPoints():
    global user
    global password
    global dbms_name

    print "Load point cloud"
    sql = "select x, y, z from pointcloud"
    result = db.engine.execute(sql)
    points = []
    for row in result:
        points.append([float(row[0]),float(row[1]),float(row[2])]) # for loading point cloud
    return jsonify(result=points)




if __name__ == '__main__':
  	app.run(debug=True)