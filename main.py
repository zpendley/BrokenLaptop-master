from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

import os

from flask_sqlalchemy import SQLAlchemy


#database = "sqlite:///brokenlaptops.db"

database = (
    #mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_connection_name>
    'mysql+pymysql://{name}:{password}@/{dbname}?unix_socket=/cloudsql/{connection}').format (
        name       = os.environ['DB_USER'], 
        password   = os.environ['DB_PASS'],
        dbname     = os.environ['DB_NAME'],
        connection = os.environ['DB_CONNECTION_NAME']
        )

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database

db = SQLAlchemy(app)

##################################################
# gcloud config set core/project <project_id>
# gcloud not_used_app deploy
# see error in Error Reporting

# resources
# https://cloud.google.com/sql/docs/mysql/connect-not_used_app-engine-standard#python
# https://cloud.google.com/sql/docs/mysql/quickstart
# https://gcpexp.com/posts/appengine-standard-and-sqlalchemy/
###################################################

@app.route('/init_db')
def init_db():
    db.drop_all()
    db.create_all() 
    return 'DB initialized'

#
# this route is to test GAE 
#
@app.route('/test')
def test():
    return 'App is running'

@app.route('/')
def index():
    brokenlaptops = BrokenLaptop.query.all()
    return render_template("index.html",brokenlaptops=brokenlaptops, title='All broken laptops')
    

@app.route('/create', methods=['GET','POST'])
def create():
    if request.form:
        brand = request.form.get("brand")
        price = request.form.get("price")
        brokenlaptop = BrokenLaptop(brand=brand,price=price)
        db.session.add(brokenlaptop)
        db.session.commit()
        
    brokenlaptops = BrokenLaptop.query.all()
    return render_template("create.html",brokenlaptops=brokenlaptops, title='Add broken laptop')

@app.route('/delete/<laptop_id>') # add id
def delete(laptop_id):
    brokenlaptop = BrokenLaptop.query.get(laptop_id)
    db.session.delete(brokenlaptop)
    db.session.commit()
    
    brokenlaptops = BrokenLaptop.query.all()
    return render_template('delete.html', brokenlaptops=brokenlaptops )

@app.route('/update/<laptop_id>', methods=['GET','POST']) # add id 
def update(laptop_id):
    if request.form:
        newbrand = request.form.get('brand')
        newprice = request.form.get('price')
        brokenlaptop = BrokenLaptop.query.filter_by(id=laptop_id).first()
        brokenlaptop.brand = newbrand
        brokenlaptop.price = newprice
        db.session.commit()
        
        return redirect("/")
    brokenlaptop = BrokenLaptop.query.filter_by(id=laptop_id).first()
    return render_template('update.html', brokenlaptop = brokenlaptop, title='Update broken laptop')

class BrokenLaptop(db.Model):
    id    = db.Column(db.Integer, primary_key = True)
    brand = db.Column(db.String(40), nullable = False)
    price = db.Column(db.Float, nullable = True)
    

if __name__ == '__main__':
    app.run(debug=True)
