from flask import Flask, render_template, request, redirect, url_for, flash, session
import segno
from nanoid import generate
import sqlite3
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generateQr():
    unique_id = generate(size=10)
    conn = sqlite3.connect('./attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO session (session_code) VALUES ('{}')".format(unique_id))
    conn.commit()
    conn.close()
    return render_template('attendance-qr.html', qr=segno.make(f'http://localhost:5000/attendee/{unique_id}').svg_data_uri(scale=5),attendee_link=f'./attendee/{unique_id}', host_id=unique_id)

@app.route('/attendee/<string:host_id>', methods=['GET','POST'])
def attendee(host_id):
    if request.method == 'GET':
        conn = sqlite3.connect('./attendance.db')
        c = conn.cursor()
        c.execute("SELECT * FROM session WHERE session_code = '{}'".format(host_id))
        data = c.fetchone()
        conn.close()
        if data == None:
            return redirect(url_for('index'))
        return render_template('./attendee/attendee-template.html',has_attended="False" , host_id=host_id,host_id_link=f'/attendee/{host_id}')
    elif request.method == 'POST':
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO session_data (session_code, name,email) VALUES ('{}','{}','{}')".format(host_id,request.form['name'],request.form['email']))
        conn.commit()
        conn.close()
    return render_template('./attendee/attendee-form.html',has_attended="True")


if __name__ == '__main__':
    app.run(debug=True)