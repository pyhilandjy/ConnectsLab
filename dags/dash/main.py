from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'jun'
app.config['MYSQL_PASSWORD'] = '1234qwer'
app.config['MYSQL_DB'] = 'STT'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    selected_date = request.form['date']
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cur.execute("SELECT user_id, user_name, text, confidence, speaker_label, text_edited, date, unique_id FROM STT WHERE DATE(date) = %s", (selected_date,))
    data = cur.fetchall()
    cur.close()
    html = ''
    for row in data:
        html += f'<tr data-unique-id="{row["unique_id"]}">'
        html += f'<td>{row["user_name"]}</td>'
        html += f'<td>{row["text"]}</td>'
        html += f'<td><input type="text" class="text-edited" value="{row["text_edited"]}"></td>'
        html += f'<td>{row["confidence"]}</td>'
        html += f'<td>{row["speaker_label"]}</td>'
        html += f'<td>{row["date"]}</td>'
        html += '</tr>'
    return html

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()['data']
    cur = mysql.connection.cursor()
    for item in data:
        unique_id = item['uniqueId']
        text_edited = item['textEdited']
        cur.execute("UPDATE STT SET text_edited = %s WHERE unique_id = %s", (text_edited, unique_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'status': 'success'})


@app.route('/get_usernames', methods=['POST'])
def get_usernames():
    selected_date = request.form['date']
    cur = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    query = "SELECT DISTINCT user_name FROM STT WHERE DATE(date) = %s"
    cur.execute(query, (selected_date,))
    user_names = cur.fetchall()
    cur.close()
    return jsonify(user_names)


if __name__ == "__main__":
    app.run(debug=True)
