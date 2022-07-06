import sqlite3
import logging

from flask import Flask, request, render_template, flash, \
    redirect, session
from redis import RedisCluster

# server config
DATA_DB = 'game.db'
SECRET_KEY = 'jui*Ojl90G'

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY


class DB:
    """
    use sqlite to persist data.
    """

    def __init__(self):
        self.db = DATA_DB

    def create_table(self):
        """
        create a table for searchitem.
        """
        # check exist table
        self.drop_db()
        sql = """
        CREATE TABLE {} (
           _id INTEGER PRIMARY KEY AUTOINCREMENT,
           column_1 NUMERIC,
           column_2 NUMERIC,
           column_3 NUMERIC,
           name CHARACTER(20)
        );
        """.format(self.table)
        self.execute(sql)

    def drop_db(self):
        """
        drop voting table
        """
        sql = 'drop table if exists {};'.format(self.table)
        self.execute(sql)

    def execute(self, sql, args=None):
        """
        do execute sql
        """
        print(sql, args)

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        try:
            if args is not None:
                c.execute(sql, args)
            else:
                c.execute(sql)
            conn.commit()
            res = c.fetchall()
            return res
        except Exception as e:
            logging.error(e)
        finally:
            conn.close()

    def get_items(self, limit=None):
        """
        get all items
        """
        sql = "SELECT * FROM {};".format(self.table)
        if limit:
            sql += " limit {};".format(limit)
        res = self.execute(sql)
        return res

    def str_to_num(self, s):
        """
        convert str num to float
        """
        if isinstance(s, str):
            return int(float(s))
        return s


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        play_name = ''
        code = ''
        if code != '':
            flash()
            return redirect('/')
        
        if user_name == 'admin' and role == 'admin':
            return redirect('/admin')

        if role == 'player':
            return redirect('/player')

    user_name = session.get('username')
    role = session.get('role')
    if user_name is None:
        game_status = ''
        if game_status == 'RUNNING':
            flash('can not join')
            return render_template('index.html')

    if user_name == 'admin' and role == 'admin':
        return redirect('/admin')

    if role == 'player':
        return redirect('/player')

    return render_template('index.html')


@app.route('/admin')
def admin():
    games = []
    players = ['matrix', 'qin']
    cur_games_remains = 10
    return render_template('admin.html', players=players)


@app.route('/player')
def player():
    return render_template('player.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
