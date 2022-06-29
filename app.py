import os
import csv
import sqlite3
import logging

from flask import Flask, request, render_template, flash, \
    redirect

# server config
DATA_DB = 'fruit.db'
TABLE = 'fruit'
DATA_FILE = 'fruit.csv'
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

    def load_data(self):
        """
        load csv data to sqlite
        """
        with open(DATA_FILE) as f:
            reader = csv.reader(f)
            # skip csv header line
            # next(reader)
            for row in reader:
                r = [
                    self.str_to_num(self.str_to_num(row[0])), 
                    self.str_to_num(self.str_to_num(row[1])), 
                    self.str_to_num(self.str_to_num(row[2])),
                    row[3]
                ]
                sql = """
                INSERT INTO {} (
                column_1,column_2,column_3,name)
                VALUES (?,?,?,?)
                """.format(self.table)
                self.execute(sql, r)

    def str_to_num(self, s):
        """
        convert str num to float
        """
        if isinstance(s, str):
            return int(float(s))
        return s

    def get_fruit_count(self, fruit_names):
        """
        get state total pop
        """
        rv = [['fruit', 'count']]
        for name in fruit_names:
            sql = "SELECT COUNT(*) FROM {} WHERE name=?".format(self.table)
            res = self.execute(sql,(name,))
            rv.append([name, res[0][0]])
        return rv

    def get_top_n(self, top_number):
        print(top_number)
        rv = [['fruit', 'count']]
        sql = "SELECT name, COUNT(*) FROM {} GROUP BY name ORDER BY COUNT(*) DESC".format(self.table)
        res = self.execute(sql,)
        res = res[:top_number]
        for r in res:
            rv.append([r[0], r[1]])
        print(rv)
        return rv

    def get_scatter(self, low, high):
        print(low, high)
        rv = [['X', 'Y']]
        sql = "SELECT column_1, column_3 FROM {} WHERE column_1>=? AND column_1<=?".format(self.table)
        res = self.execute(sql, (low, high))
        for r in res:
            print(r[0], r[1])
            rv.append([r[0], r[1]])
        print(rv)
        return rv



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


@app.route('/fruit_fraction', methods=['POST'])
def fruit_count():
    """
    return fruit fraction, resp json: {"data": [], "error": {"code": 0, "msg": ""}}
    """
    data = request.json
    fruit_names = data.get('fruit_names').split(',')
    rv = DB().get_fruit_count(fruit_names)
    return {
        'data': rv,
        'error': {
            'code': 0,
            'msg': ''
        }
    }


@app.route('/top_n', methods=['POST'])
def top_n():
    """
    return top n, resp json: {"data": [], "error": {"code": 0, "msg": ""}}
    """
    data = request.json
    top_number = data.get('top_number')
    rv = DB().get_top_n(top_number)
    return {
        'data': rv,
        'error': {
            'code': 0,
            'msg': ''
        }
    }


@app.route('/draw_scatter_diagram', methods=['POST'])
def scatter_diagram():
    """
    return top n, resp json: {"data": [], "error": {"code": 0, "msg": ""}}
    """
    data = request.json
    print(data)
    low = data.get('low')
    high = data.get('high')
    rv = DB().get_scatter(low, high)
    return {
        'data': rv,
        'error': {
            'code': 0,
            'msg': ''
        }
    }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
