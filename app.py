from flask import Flask, request, render_template ,redirect, url_for, jsonify
import sqlite3
import json

import logging

 
app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.DEBUG)




def get_db_connection():
    conn = sqlite3.connect('mydatabase.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('login.html')
@app.route('/admin_profile/' ,methods=['GET'])
def admin_profile():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()

        return render_template('admin_info.html',campaigns=campaigns)

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/logout/',methods=['POST'])
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
            #inserting data 
            company_name = request.form['company_name']
            budget = request.form['budget']
            industry = request.form['industry']
            username = request.form['username']
            password = request.form['password']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO sponsor (company_name, budget, industry, username, password,flagged ) VALUES (?, ?, ?, ?, ?,?)", (company_name, budget, industry, username, password,0))
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
            niche=request.form['niche']
            #establish connection
            conn = get_db_connection()
            cur = conn.cursor()
            #Now inserting data
            cur.execute("INSERT INTO influencer (influencer_name, target_audience, youtube, instagram, twitter, username, password,Earning,flagged,niche) VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?)", (influencer_name, target_audience, youtube, instagram, twitter, username, password,0,0,niche))
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
    cur.execute("SELECT * FROM campaigns ")
    
    campaigns = cur.fetchall()
    active_earnings = int((sum(campaign['budget'] for campaign in campaigns if campaign['influencer_decision'] == 'accept' and campaign['sponsor_decision'] == influencer['username'] and campaign['flagged'] == 0 and campaign['visibility'] == 'public')))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE influencer SET Earning = ? WHERE username = ?', (active_earnings,username,))
    conn.commit()
    conn.close()
    if influencer and influencer['password']==Inf_password:
        return render_template('influ_dashboard.html' ,influencer=influencer ,campaigns=campaigns ,active_earnings=active_earnings) 
    else:
        return "login failed!"


@app.route('/inf_stats/', methods=['POST'])
def inf_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT influencer_name, Earning FROM influencer;"
    data = conn.execute(query).fetchall()

    conn.close()

    labels = [row[0] for row in data]
    earnings = [row[1] for row in data]
    
    return render_template('inf_stats.html', labels=json.dumps(labels), earnings=json.dumps(earnings))




@app.route('/update_profile/<string:username>/', methods=['POST'])
def update_profile(username):
    influencer_name = request.form['influencer_name']
    target_audience = request.form['target_audience']
    password=request.form['password']
    twitter = request.form.get('twitter') == '1'
    youtube = request.form.get('youtube') == '1'
    instagram = request.form.get('instagram') == '1'
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaigns ")

    campaigns = cur.fetchall()
    active_earnings = int((sum(campaign['budget'] for campaign in campaigns if campaign['influencer_decision'] == 'accept' and campaign['sponsor_decision'] == username and campaign['flagged'] == 0 and campaign['visibility'] == 'public')))
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE influencer SET influencer_name=?, target_audience=?, Earning=?, password=?, twitter=?, youtube=?, instagram=? WHERE username= ? ', (influencer_name, target_audience, active_earnings, password, twitter, youtube, instagram, username))
    conn.commit()
    
    conn.close()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM influencer WHERE username = ?", (username,))
    influencer = cur.fetchone()
    cur.execute("SELECT * FROM campaigns ")
    campaigns = cur.fetchall()
    conn.close()
    return render_template('influ_dashboard.html' ,influencer=influencer ,campaigns=campaigns,active_earnings=active_earnings ) 
    


@app.route('/accept/<int:campaign_id>/<int:influencer_id>/', methods=['POST'])
def accept(campaign_id,influencer_id):
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('UPDATE campaigns SET influencer_decision = ? WHERE id = ?', ('accept' ,campaign_id,))
        conn.commit()
        conn.close
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM influencer WHERE id = ?", (influencer_id,))
        influencer = cur.fetchone()
        conn.close()
        return render_template('influ_dashboard.html' ,influencer=influencer ,campaigns=campaigns ) 



@app.route('/reject/<int:campaign_id>/<int:influencer_id>/', methods=['POST'])
def reject(campaign_id,influencer_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE campaigns SET influencer_decision = ? WHERE id = ?', ('reject',campaign_id,))
        conn.commit()
        conn.close
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM influencer WHERE id = ?", (influencer_id,))
        influencer = cur.fetchone()
        conn.close()
        return render_template('influ_dashboard.html' ,influencer=influencer ,campaigns=campaigns ) 








@app.route('/create_campaigns/<int:sponsor_id>/', methods=['GET'])
def create_campaigns(sponsor_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()  
        # conn = get_db_connection()
        # cur = conn.cursor()
        # cur.execute("SELECT * FROM sponsor ")
        # sponsor = cur.fetchall()
        # conn.close()

        return render_template('create_campaigns.html',campaigns=campaigns,sponsor_id=sponsor_id)


@app.route('/ADD/',methods=['POST'])
def ADD():
     if request.method=='POST':
        
               
            sponsor_id = request.form['sponsor_id']
            name = request.form['campaign_name']
            description = request.form['description']
            budget = request.form['budget']
            start_date = request.form['start-date']
            end_date = request.form['end-date']
            visibility=request.form['visibility']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO campaigns (name, description, budget ,start_date,end_date,visibility,sponsor_id,image,status,flagged,influencer_decision,sponsor_decision) VALUES (?, ?, ?, ?, ?,?,?,?,?,?,?,?)',
                            (name, description, budget,start_date,end_date, visibility,sponsor_id,'null','Active',0,'pending','null'))
            conn.commit()
            msg="Campaign Added successfully check it on our dashboard !!!"
            return msg

@app.route('/viewads/<int:campaign_id>', methods=['POST'])
def viewads(campaign_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ads WHERE campaign_id = ?", (campaign_id,))
    ads = cur.fetchall()
    cur.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM influencer ")
    influencer = cur.fetchall()
    conn.close()



    return render_template('campaign_ad.html',ads=ads,campaign_id=campaign_id,influencer=influencer)



@app.route('/ads/<int:campaign_id>/', methods=['POST'])
def ads(campaign_id):
    try :
        msg = 'empty'

        ad_name = request.form['ad_name']
        
        terms = request.form['terms']
        
        budget = request.form['budget']
        # image = request.files['image'] 
        description = request.form['description']
        influencer_name=request.form['influencer_name']
        conn = sqlite3.connect('mydatabase.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
       
        
        cur = conn.cursor()
        cur.execute('INSERT INTO ads (ad_name, description, budget , terms,campaign_id,influencer_name) VALUES (?, ?, ?, ?, ?,?)',
                            (ad_name, description, budget, terms,campaign_id,influencer_name))
        conn.commit()
        conn.close()
        logging.info("ad added successfully")
       
        msg='ads created successfully !!! '
        conn.close()
        
        return msg
    except Exception as e:
        logging.error(f"Error: {e}")
        msg='Error while creating ad try again later !!!'
        return msg

        
@app.route('/info/', methods=['GET','POST'])
def info():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template("admin_info.html" ,campaigns=campaigns)



@app.route('/flag/<int:campaign_id>/', methods=['POST'])
def flag(campaign_id):
     
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE campaigns SET flagged = 1 WHERE id = ?', (campaign_id,))
        conn.commit()
        conn.close
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()

        conn.close()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM sponsor')
        sponsor = cur.fetchall()
        conn.close()

        return render_template("admin_info.html",campaigns=campaigns,sponsor=sponsor)



@app.route('/unflag/<int:campaign_id>/', methods=['POST'])
def unflag(campaign_id):
     
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE campaigns SET flagged = 0 WHERE id = ?', (campaign_id,))
        conn.commit()
        conn.close
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()
        return render_template("admin_info.html",campaigns=campaigns)



@app.route('/unflag_sponsor/<string:username>/', methods=['POST'])
def unflag_sponsor(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE sponsor SET flagged = 0 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()

    return render_template("admin_find_dashboard.html", sponsor=sponsor, influencer=influencer)




@app.route('/flag_sponsor/<string:username>/', methods=['POST'])
def flag_sponsor(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE sponsor SET flagged = 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()

    return render_template("admin_find_dashboard.html", sponsor=sponsor, influencer=influencer)




@app.route('/unflag_inf/<string:username>/', methods=['POST'])
def unflag_inf(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE influencer SET flagged = 0 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()

    return render_template("admin_find_dashboard.html", sponsor=sponsor, influencer=influencer)




@app.route('/flag_inf/<string:username>/', methods=['POST'])
def flag_inf(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE influencer SET flagged = 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()

    return render_template("admin_find_dashboard.html", sponsor=sponsor, influencer=influencer)







@app.route('/campaign_edit/<int:campaign_id>/<int:sponsor_id>/', methods=['POST'])
def campaign_edit(campaign_id, sponsor_id):
        name = request.form['name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        description = request.form['description']
        visibility = request.form['visibility']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE campaigns SET name = ?, description = ?, start_date = ?, end_date = ?,visibility =? WHERE id = ?
        ''', (name, description, start_date, end_date,visibility, campaign_id))
        
        conn.commit()
        conn.close()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM sponsor WHERE id = ?", (sponsor_id,))
        sponsor = cur.fetchone()
        conn.close()

        logging.info("Campaign Updated successfully!")
        return render_template('sponsor_das.html', campaigns=campaigns, sponsor=sponsor)
   

@app.route('/find_cam_inf/<int:sponsor_id>', methods=['GET', 'POST'])
def find_cam_inf(sponsor_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template('campaigns_inffind.html', campaigns= campaigns,sponsor_id=sponsor_id)


@app.route('/requested/<string:username>/', methods=['POST'])
def requested(username):
        conn = get_db_connection()
        cur = conn.cursor()
        name = request.form['name']
        cur.execute('UPDATE campaigns SET sponsor_decision = ? WHERE name = ?', (username ,name,))
        conn.commit()
        conn.close()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM campaigns')
        campaigns = cur.fetchall()
        conn.close()
     

        return render_template('campaigns_inffind.html' ,campaigns=campaigns)



@app.route('/find_campaigns_influencer/', methods=['POST'])
def find_campaigns_influencer():
    conn = get_db_connection()
    cur = conn.cursor()
    results=[]
    if request.method == 'POST':
        search = request.form.get('search')
        cam_inf=request.form.get('cam_inf')
        cam=0
        inf=0
        if cam_inf == 'influencers' :
            filter_type = request.form.get('filter')
            
            if filter_type == 'name':
                cur.execute("SELECT * FROM influencer WHERE influencer_name LIKE ?", ('%' + search + '%',))
            elif filter_type == 'niche':
                cur.execute("SELECT * FROM influencer WHERE niche LIKE ?", ('%' + search + '%',))
            else:
                cur.execute("SELECT * FROM influencer")
            inf=1
            results = cur.fetchall()
        if cam_inf == 'campaigns' :
            filter_type = request.form.get('filter')
            if filter_type == 'name':
                cur.execute("SELECT * FROM campaigns WHERE name LIKE ?", ('%' + search + '%',))
            else :
                cur.execute("SELECT * FROM campaigns")
            cam=1
            results = cur.fetchall()
    else:
        cur.execute("SELECT * FROM influencer")
        results = cur.fetchall()
    
    conn.close()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template('campaigns_inffind.html', results=results,cam=cam,inf=inf,campaigns=campaigns)




@app.route('/find_campaigns_ads/', methods=['POST'])
def find_campaigns_ads():
    conn = get_db_connection()
    cur = conn.cursor()
    results=[]
    if request.method == 'POST':
        search = request.form.get('search')
        cam_ads=request.form.get('cam_ads')
        cam=0
        ads=0
        if cam_ads == 'ads' :
            
            cur.execute("SELECT * FROM ads WHERE ad_name LIKE ?", ('%' + search + '%',))
           
            ads=1
            results = cur.fetchall()
        if cam_ads == 'campaigns' :
           
            cur.execute("SELECT * FROM campaigns WHERE name LIKE ?", ('%' + search + '%',))
            
            cam=1
            results = cur.fetchall()
    conn.close()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    
    return render_template('admin_info.html', results=results,cam=cam,ads=ads,campaigns=campaigns)



@app.route('/find_camads/<int:influencer_id>/', methods=['POST'])
def find_camads(influencer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template('inf_finddashboard.html',campaigns=campaigns,influencer_id=influencer_id)





@app.route('/influencer_campaigns_ads/<int:influencer_id>', methods=['POST'])
def influencer_campaigns_ads(influencer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    results=[]
    if request.method == 'POST':
        search = request.form.get('search')
        cam_ads=request.form.get('cam_ads')
        cam=0
        ads=0
        if cam_ads == 'ads' :
            
            cur.execute("SELECT * FROM ads WHERE ad_name LIKE ?", ('%' + search + '%',))
           
            ads=1
            results = cur.fetchall()
        if cam_ads == 'campaigns' :
           
            cur.execute("SELECT * FROM campaigns WHERE name LIKE ?", ('%' + search + '%',))
            
            cam=1
            results = cur.fetchall()
    conn.close()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM campaigns')
    campaigns = cur.fetchall()
    conn.close()
    return render_template('inf_finddashboard.html', results=results,cam=cam,ads=ads,campaigns=campaigns,influencer_id=influencer_id)








@app.route('/find_sponsors_influencer/', methods=['POST'])
def find_sponsors_influencer():
    conn = get_db_connection()
    cur = conn.cursor()
    results=[]
    inf=0
    spo=0
    if request.method == 'POST':
        search = request.form.get('search')
        spo_inf=request.form.get('spo_inf')
        
        
        if spo_inf == 'influencers' :
            inf=1
            cur.execute("SELECT * FROM influencer WHERE influencer_name LIKE ?", ('%' + search + '%',))
           
            
            results = cur.fetchall()
        if spo_inf == 'sponsors' :
            spo=1
            cur.execute("SELECT * FROM sponsor WHERE company_name LIKE ?", ('%' + search + '%',))
            
            results = cur.fetchall()
    
    
    conn.close()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sponsor')
    sponsor = cur.fetchall()
    
    cur.execute('SELECT * FROM influencer')
    influencer = cur.fetchall()
    conn.close()
    return render_template('admin_find_dashboard.html', sponsor=sponsor, influencer=influencer,results=results,inf=inf,spo=spo)



@app.route('/admin_stats/', methods=['GET','POST'])
def admin_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT company_name, budget FROM sponsor;"
    data = conn.execute(query).fetchall()

    conn.close()

    labels = [row[0] for row in data]
    budgets = [row[1] for row in data]

    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT influencer_name, Earning FROM influencer;"
    data = conn.execute(query).fetchall()

    conn.close()

    labels_1 = [row[0] for row in data]
    earnings = [row[1] for row in data]
    conn = get_db_connection()
    query = "SELECT name, budget FROM campaigns;"
    data = conn.execute(query).fetchall()

    conn.close()

    labels_2 = [row[0] for row in data]
    budget = [row[1] for row in data]







    
    return render_template('admin_stats.html', labels=json.dumps(labels), budgets=json.dumps(budgets), labels_1=json.dumps(labels_1), earnings=json.dumps(earnings),labels_2=json.dumps(labels_2), budget=json.dumps(budget))

@app.route('/sponsor_stats', methods=['GET','POST'])
def sponsor_budget():
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT company_name, budget FROM sponsor;"
    data = conn.execute(query).fetchall()

    conn.close()

    labels = [row[0] for row in data]
    budgets = [row[1] for row in data]

    
    return render_template('sponsor_stats.html', labels=json.dumps(labels), budgets=json.dumps(budgets))


if __name__ == '__main__':
    app.run(debug=True)
