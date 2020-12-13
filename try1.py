from flask import Flask, request, jsonify, redirect, url_for, session, render_template
from flaskext.mysql import MySQL
from flask_oauth import OAuth
import logging
import time
from logging.handlers import RotatingFileHandler
# library request buat dapatin bodynya gitu
# ngereturn json, biar hasilnya itu bagus

oauth = OAuth()
app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'secretkey'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'tstnaomi'
app.config['MYSQL_DATABASE_HOST'] = '172.24.0.2'
app.config['MYSQL_DATABASE_PORT'] = 3306
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

mysql.init_app(app)
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key='287118996837-n4iu5m6o25cln3266o257rbi6f5btqbo.apps.googleusercontent.com',
                          consumer_secret='yUfDIywpy_4f7olXPtB3SPDY')

# yang penting ada routenya
# HTTP request method: GET, POST, PUT, DELETE
# umumnya dipake yang GET POST
 
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home', methods =  ['GET'])
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    # cursor buat melakukan perintah2
    query = 'SELECT * FROM tugas'

    cursor.execute(query)
    result = cursor.fetchall()
    # dari mysql hasilnya langsung list, tapi listnya double

    result_baru = []
    for tugas in result:
        tugas_baru = {
            'id': tugas[0],
            'mata_kuliah': tugas[1],
            'deskripsi': tugas[2],
            'deadline': tugas[3],
            'status': tugas[4]
        }
        result_baru.append(tugas_baru)
    conn.commit()
    conn.close()
    cursor.close()

    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ ' Akses home')
    return render_template('index.html', data=result)

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/authorized')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    # session['access_token'] = access_token, ''
    print(access_token)
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@app.route('/tugas', methods=['GET'])
def get_tugas():
    # data = ['alya', 'nomi', 'abeth']
    # users = {
    #     'status': 'sukses',
    #     'message': 'ini hasilnya',
    #     'data': data
    #     # sabi diganti apapun
    # }

    # skrg from database
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    # cursor buat melakukan perintah2
    query = 'SELECT * FROM tugas'

    cursor.execute(query)
    result = cursor.fetchall()
    # dari mysql hasilnya langsung list, tapi listnya double

    result_baru = []
    for tugas in result:
        tugas_baru = {
            'id': tugas[0],
            'mata_kuliah': tugas[1],
            'deskripsi': tugas[2],
            'deadline': tugas[3],
            'status': tugas[4]
        }
        result_baru.append(tugas_baru)

    # Ngereturn dalam bentuk json
    # return jsonify(users)
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ ' Akses get tugas')
    return {'hasil': result_baru}
    # list: data[0] data[1]
    # json/dictionary: data['nama']

@app.route('/create', methods=['POST'])
def insert_tugas():
    # data = ['alya', 'nomi', 'abeth']
    # users = {
    #     'status': 'sukses',
    #     'message': 'ini hasilnya',
    #     'data': data
    #     # sabi diganti apapun
    # }

    # skrg from database
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    mata_kuliah = request.form['mata_kuliah']
    deskripsi = request.form['deskripsi']
    deadline = request.form['deadline']
    status = request.form['status']
    # cursor buat melakukan perintah2
    query = 'INSERT INTO tugas (mata_kuliah, deskripsi, deadline, status) VALUES (%s, %s, %s, %s)'
    data = (mata_kuliah, deskripsi, deadline, status)

    cursor.execute(query, data)
    conn.commit()
    conn.close()

    result = {
        'mata_kuliah': mata_kuliah,
        'deskripsi': deskripsi,
        'deadline': deadline,
        'status' : status
    }
    # dari mysql hasilnya langsung list, tapi listnya double

    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ ' Akses tambah tugas')
    return {'hasil': result}
    # list: data[0] data[1]
    # json/dictionary: data['nama']

@app.route('/update', methods=['PUT'])
def update_status():
    # data = ['alya', 'nomi', 'abeth']
    # users = {
    #     'status': 'sukses',
    #     'message': 'ini hasilnya',
    #     'data': data
    #     # sabi diganti apapun
    # }

    # skrg from database
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    id = request.form['id']
    statusbaru = request.form['status']
    # cursor buat melakukan perintah2
    query = 'UPDATE tugas SET status = %s WHERE id = %s'
    data = (statusbaru, id)

    cursor.execute(query, data)
    conn.commit()
    conn.close()

    result = {
        'Data berhasil diubah menjadi' : statusbaru
    }
    # dari mysql hasilnya langsung list, tapi listnya double

    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ ' Akses update tugas')
    return {'hasil': result}
    # list: data[0] data[1]
    # json/dictionary: data['nama']

@app.route('/delete', methods=['DELETE'])
def delete_tugas():
    # data = ['alya', 'nomi', 'abeth']
    # users = {
    #     'status': 'sukses',
    #     'message': 'ini hasilnya',
    #     'data': data
    #     # sabi diganti apapun
    # }

    # skrg from database
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    conn = mysql.connect()
    cursor = conn.cursor()
    id = request.form['id']
    # cursor buat melakukan perintah2

    query = 'DELETE FROM tugas WHERE id = %s'
    data = id

    cursor.execute(query, data)
    conn.commit()
    conn.close()

    # dari mysql hasilnya langsung list, tapi listnya double

    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ ' Akses hapus tugas')
    return "Data berhasil dihapus"
    # list: data[0] data[1]
    # json/dictionary: data['nama']

# nandain program utama ini main, terus di-assign ke flask
if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')