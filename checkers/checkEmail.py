import json
from sql_conn import mysql_conn


def check_email(msg_received):
    email = str(msg_received["email"])

    if email == '0':
        return json.dumps({'phone': '0'})

    conn = mysql_conn.create()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM `users` WHERE `email`= %s ;", (email,))
    row = cursor.fetchall()

    if len(row) != 0:
        conn.close()
        cursor.close()
        return json.dumps({'email': '1'})

    else:
        conn.close()
        cursor.close()
        return json.dumps({'email': '0'})
