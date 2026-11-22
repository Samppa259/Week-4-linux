
import os
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

def get_connection():
    return pymysql.connect(
    unix_socket="/run/mysqld/mysqld.sock",
    user="week2counter",
        password=os.environ["DB_PASSWORD"],
        database="week2db"
    )

@app.route("/")
def home():
    return "Viikko2 Python server is running!"

@app.route("/counter")
def counter():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE visitors SET count = count + 1 WHERE id = 1"
            )
            connection.commit()

            cursor.execute(
                "SELECT count FROM visitors WHERE id = 1"
            )
            result = cursor.fetchone()

            return jsonify({"visitors": result[0]})
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

