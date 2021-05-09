from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flask_socketio import SocketIO
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'OscarsMale'
app.config['SECRET_KEY'] = 'asdfghjkl'
socketio = SocketIO(app)
mysql.init_app(app)

events = [
    {
        'todo' : 'Final Project',
        'date' : '2021-05-10',
    }
]


@app.route('/', methods=['GET'])
def index():
    user = {'username': 'Oscars Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblOscarsImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, oscars=result)

@app.route('/oscars/session')
def sessions():
    return render_template('session.html', methods=['GET', 'POST'])

def messageReceived():
    print('message was received!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/view/<int:oscar_id>', methods=['GET'])
def record_view(oscar_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblOscarsImport WHERE id=%s', oscar_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', oscar=result[0])


@app.route('/edit/<int:oscar_id>', methods=['GET'])
def form_edit_get(oscar_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblOscarsImport WHERE id=%s', oscar_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', oscar=result[0])


@app.route('/edit/<int:oscar_id>', methods=['POST'])
def form_update_post(oscar_id):
    cursor = mysql.get_db().cursor()
    input_data = (request.form.get('Indx'), request.form.get('Years'), request.form.get('Ages'),
                  request.form.get('Actor'), request.form.get('Movie'),
                  request.form.get('Column_6'), oscar_id)
    sql_update_query = """UPDATE tblOscarsImport t SET t.Indx = %s, t.Years = %s, t.Ages = %s, t.Actor = 
    %s, t.Movie = %s, t.Column_6 = %s  WHERE t.id = %s """
    cursor.execute(sql_update_query, input_data)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/oscars/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Oscars Form')


@app.route('/oscars/calendar', methods=['GET'])
def form_calendar_get():
    return render_template('calendar.html', events=events, title='Calendar')


@app.route('/oscars/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    input_data = (request.form.get('Indx'), request.form.get('Years'), request.form.get('Ages'),
                  request.form.get('Actor'), request.form.get('Movie'),
                  request.form.get('Column_6'))
    sql_insert_query = """INSERT INTO tblOscarsImport (Indx,Years,Ages,Actor,Movie,Column_6)VALUES(%s,%s,%s,%s,%s,%s)"""
    cursor.execute(sql_insert_query, input_data)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:oscar_id>', methods=['POST'])
def form_delete_post(oscar_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblOscarsImport WHERE id = %s """
    cursor.execute(sql_delete_query, oscar_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/oscars', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblOscarsImport')
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/oscars/<int:oscar_id>', methods=['GET'])
def api_retrieve(oscar_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblOscarsImport WHERE id=%s', oscar_id)
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/oscars/', methods=['POST'])
def api_add() -> str:
    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['Indx'], content['Years'], content['Ages'],
                 content['Actor'], content['Movie'],
                 content['Column_6'])
    sql_insert_query = """INSERT INTO tblOscarsImport (Indx,Years,Ages,Actor,Movie,Column_6) VALUES (%s, %s,%s, %s,%s, %s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/oscars/<int:oscar_id>', methods=['PUT'])
def api_edit(oscar_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Indx'], content['Years'], content['Ages'],
                 content['Actor'], content['Movie'],
                 content['Column_6'], oscar_id)
    sql_update_query = """UPDATE tblOscarsImport t SET t.Indx = %s, t.Years = %s, t.Ages = %s, t.Actor = 
                %s, t.Movie = %s, t.Column_6 = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/oscars/<int:oscar_id>', methods=['DELETE'])
def api_delete(oscar_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblOscarsImport WHERE id = %s """
    cursor.execute(sql_delete_query, oscar_id)
    mysql.get_db().commit()
    resp = Response(status=210, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

