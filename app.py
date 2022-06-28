import os
import csv
import sqlite3
import logging

from flask import Flask, request, render_template, flash, \
    redirect

# server config
DATA_DB = 'voting.db'
TABLE = 'voting'
DATA_FILE = 'voting.csv'
SECRET_KEY = 'jui*Ojl90G'
UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = ['csv']

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class DB:
    """
    use sqlite to persist data.
    """

    def __init__(self):
        self.db = DATA_DB
        self.table = TABLE

    def create_table(self):
        """
        create a table for searchitem.
        """
        # check exist table
        self.drop_db()
        sql = """
        CREATE TABLE {} (
           _id INTEGER PRIMARY KEY AUTOINCREMENT,
           state_name INT,
           total_pop INT,
           vote_pop INT,
           registered INT,
           voted INT
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

    def load_data(self):
        """
        load csv data to sqlite
        """
        with open(DATA_FILE) as f:
            reader = csv.reader(f)
            # skip csv header line
            next(reader)
            for row in reader:
                r = [
                    row[0], 
                    self.str_to_num(self.str_to_num(row[1])), 
                    self.str_to_num(self.str_to_num(row[2])), 
                    self.str_to_num(self.str_to_num(row[3])),
                    self.str_to_num(self.str_to_num(row[4]))
                ]
                sql = """
                INSERT INTO {} (
                state_name,total_pop,vote_pop,registered,voted)
                VALUES (?,?,?,?,?)
                """.format(self.table)
                self.execute(sql, r)

    def str_to_num(self, s):
        """
        convert 1,111 to 1111
        """
        if isinstance(s, str):
            return int(s.replace(',', ''))
        return s

    def get_total_pop(self):
        """
        get state total pop
        """
        sql = "SELECT state_name,total_pop FROM {}".format(self.table)
        res = self.execute(sql)
        # just return state_name and total_pop columns
        return [[row[0], row[1]] for row in res]

    def get_state_voted(self):
        """
        get state voted pop
        """
        sql = "SELECT state_name,voted FROM {}".format(self.table)
        res = self.execute(sql)
        return [[row[0], row[1]] for row in res]

    def get_total_voted(self):
        """
        get state total and voted pop
        """
        sql = "SELECT total_pop,voted FROM {}".format(self.table)
        res = self.execute(sql)
        return [[row[0], row[1]] for row in res]


@app.route('/')
def index():
    is_db_exist = os.path.exists(DATA_DB)
    return render_template('index.html', is_db_exist=is_db_exist)


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    upload csv file to system
    """
    if 'file' not in request.files:
        flash('please select a file firstly', category='Error')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', category='Error')
        return redirect('/')
    # check file type
    if '.' not in file.filename \
            or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        flash('Just upload csv file only.', category='Error')
        return redirect('/')

    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], DATA_FILE))
        DB().create_table()
        DB().load_data()
        flash('upload success', category='Info')
        return redirect('/')


@app.route('/delete_data', methods=['post'])
def delete_data():
    if os.path.exists(DATA_DB):
        os.remove(DATA_DB)
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    flash('Delete system data success', category='Info')
    return redirect('/')


@app.route('/state_pop')
def state_pop():
    """
    return state total pop, resp json: {"data": [], "error": {"code": 0, "msg": ""}}
    """
    total_pop = DB().get_total_pop()
    # State, totalPop as first row used for google chart to display 
    data = [['State', 'TotalPop']]
    data.extend(total_pop)
    return {
        'data': data,
        'error': {
            'code': 0,
            'msg': ''
        }
    }


@app.route('/state_voted')
def state_voted():
    """
    return state voted pop, resp json: {"data": [], "error": {"code": 0, "msg": ""}}
    """
    voted = DB().get_state_voted()
    # State, Voted as first row used for google chart to play
    data = [['State', 'Voted']]
    data.extend(voted)
    return {
        'data': data,
        'error': {
            'code': 0,
            'msg': ''
        }
    }


@app.route('/total_voted')
def total_voted():
    """
    return state total voted pop, resp json: {"data": [], "error": {"code": 0, "msg": ""}}
    """
    total_voted = DB().get_total_voted()
    # TotalPop, Voted as first row used for google chart to play
    data = [['TotalPop','Voted']]
    data.extend(total_voted)
    return {
        'data': data,
        'error': {
            'code': 0,
            'msg': ''
        }
    }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
