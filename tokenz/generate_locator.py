from tokenz import picture_code
from sql_connection import mysql_connection


# GENERATING LOCATOR
def generate():
    code = str(picture_code.user_locator())
    return check(code)


def check(code: str):
    conn = mysql_connection.create()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM `users` WHERE `locator` = %s ;'", (code,), multi=True)
    profile_row = cursor.fetchall()
    conn.close()
    cursor.close()

    if len(profile_row) == 1:

        return generate()

    else:

        return code
