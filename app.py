from flask import Flask, request, render_template ,redirect, url_for
import sqlite3

import logging

 
app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.DEBUG)




def get_db_connection():
    conn = sqlite3.connect('mydatabase.db')
    conn.row_factory = sqlite3.Row
    # conn.execute("PRAGMA foreign_keys = ON;")

    return conn

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/logout')
def logout():
    
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/sponsor_regis')
def sponsor_regis():
    return render_template('sponsor_regis.html')

@app.route('/influencer_regis')
def influencer_regis():
    return render_template('influencer_regis.html')

@app.route('/validate-admin/', methods=['POST'])
def validate_admin():
    username_admin = request.form['username']
    ad_password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin WHERE username = ?", (username_admin,))
    admin = cur.fetchone()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()
    conn.close()
    if admin and admin['password']==ad_password:
        return render_template('admin_find_dashboard.html', sponsor=sponsor, influencer=influencer)
    else:
        return render_template('admin.html', message='"Admin login failed! Please Use Correct Credentials"')
    
@app.route('/ad_dashboard')
def ad_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()
    return render_template('ad_dashboard.html',sponsor=sponsor, influencer=influencer)    

@app.route('/add-sponsor/', methods=['POST'])
def add_sponsor():
    msg = 'empty'
    
    try:
            #so we try to take the necessary data 
            company_name = request.form['company_name']
            budget = request.form['budget']
            industry = request.form['industry']
            username = request.form['username']
            password = request.form['password']
            conn = get_db_connection()
            cur = conn.cursor()
            #Now insert Data
            cur.execute("INSERT INTO sponsor (company_name, budget, industry, username, password) VALUES (?, ?, ?, ?, ?)", (company_name, budget, industry, username, password))
            conn.commit()
            msg = 'Sponsor added successfully!'
    except Exception as e:
            conn.rollback()
            msg = 'Error occurred: ' + str(e)
    finally:
        conn.close()
        return msg

@app.route('/add-influencer/', methods=['POST'])
def add_influencer():
    msg = 'empty'
    
    try:
            influencer_name = request.form['influencer_name']
            target_audience = request.form['target_audience']
            youtube = 'youtube' in request.form
            instagram = 'instagram' in request.form
            twitter = 'twitter' in request.form
            username = request.form['username']
            password = request.form['password']
            #establish connection
            conn = get_db_connection()
            cur = conn.cursor()
            #Now inserting data
            cur.execute("INSERT INTO influencer (influencer_name, target_audience, youtube, instagram, twitter, username, password) VALUES (?, ?, ?, ?, ?, ?, ?)", (influencer_name, target_audience, youtube, instagram, twitter, username, password))
            conn.commit()
            msg = 'Influencer added ! Thank You !'
    except Exception as e:
            conn.rollback()
            msg = 'Error occurred: ' + str(e)
    finally:
        conn.close()
        return msg
    

@app.route('/validate-sponsor/', methods=['POST'])
def validate_sponsor():
    username = request.form['username']
    password_Sponsor = request.form['password']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sponsor WHERE username = ?", (username,))
    sponsor = cur.fetchone()
    conn.close()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    if sponsor and sponsor['password']==password_Sponsor:
        return render_template('sponsor_das.html',sponsor=sponsor ,campaigns=campaigns )
    else:
        return "login failed!"

@app.route('/validate-influencer/', methods=['POST'])
def validate_influencer():
    username = request.form['username']
    Inf_password = request.form['password']
    #connection done
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM influencer WHERE username = ?", (username,))
    influencer = cur.fetchone()
    cur.execute("SELECT target_audience FROM influencer WHERE username = ?", (username,))
    T_a = cur.fetchone()
    conn.close()
    if influencer and influencer['password']==Inf_password:
        return render_template('influ_dashboard.html' ,influencer=influencer , T_a=T_a) 
    else:
        return "login failed!"



@app.route('/create_campaigns/', methods=['GET', 'POST'])
def create_campaigns():
        return render_template("create_campaigns.html")

# @app.route('/ADD/',methods=['POST'])
# def ADD():
#      if request.method=='POST':
#         try:
               
#             sponsor_id = request.form['id']
#             name = request.form['name']
#             description = request.form['description']
#             budget = request.form['budget']
#             start_date = request.form['start-date']
#             end_date = request.form['end-date']


@app.route('/ADD', methods=['POST'])
def add_campaign():
    try :
        name = request.form['campaign_name']
        sponsor_id = request.form['sponsor_id']
        start_date = request.form['start-date']
        end_date = request.form['end-date']
        budget = request.form['budget']
        # image = request.files['image'] 
        description = request.form['description']

        conn = sqlite3.connect('mydatabase.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
       
        
        cur = conn.cursor()
        cur.execute('INSERT INTO campaigns (sponsor_id, name, description, budget, start_date, end_date, status,image) VALUES (?, ?, ?, ?, ?, ?, ?,?)',
                            (sponsor_id, name, description, budget, start_date, end_date, 'Active','null'))
        conn.commit()
        conn.close()
        logging.info("Campaign added successfully")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()
        
        return render_template('create_campaigns.html',campaigns=campaigns)
    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template('sponsor_das.html')

        
@app.route('/info/', methods=['GET','POST'])
def info():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template("admin_info.html" ,campaigns=campaigns)



@app.route('/flag/<int:campaign_id>', methods=['GET','POST'])
def flag(campaign_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE campaigns SET flagged = 1 WHERE id = campaign_id')
    conn.commit()
    conn.close
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template("admin_info.html",campaigns=campaigns)

if __name__ == '__main__':
    app.run(debug=True)
