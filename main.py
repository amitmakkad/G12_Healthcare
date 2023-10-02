from re import A
from flask import Flask, render_template, request, session , flash
import flask
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
import mysql.connector
from flask_session import Session
from nltk.util import pr
from werkzeug.utils import redirect
import datetime
from textblob import TextBlob
import arrow
import os
from dotenv import load_dotenv
load_dotenv()
state=""

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysqlPassword = os.getenv('MYSQL_PASSWORD')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

myconn = mysql.connector.connect(host = "localhost", user = "root",passwd =mysqlPassword, database="cs207_healthcare_management", auth_plugin='mysql_native_password',buffered=True)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    try:
        session.clear()
    except:
        print("Session Not Started")
    return render_template('home.html', polarity=5.0, subjectivity=5.0)


@app.route('/hospRegisterInitial', methods=['GET', 'POST'])
def register_page_init():
    error_code = 0
    if request.method == 'POST':
        hospDetails = request.form
        hospName = hospDetails['hospName']
        hosp_ID = hospDetails['hospID']
        hospPassword = hospDetails['hospPassword']
        hospPasswordRepeat = hospDetails['hospPasswordRepeat']

        hospIDStr = str(hosp_ID)
        digCount = len(hospIDStr)
        print(digCount)

        if digCount!=5:
            return render_template('hospital_reg_init.html', error_code=4)

        if hospPassword != hospPasswordRepeat:
            error_code = 3
            return render_template('hospital_reg_init.html', error_code=error_code)

        cur = myconn.cursor()
        try:
            cur.execute("INSERT INTO Hospital(hosp_ID,hospName,hospPassword) VALUES(%s,%s,%s)",
                        (int(hosp_ID), hospName, hospPassword))
            myconn.commit()
            cur.close()
            error_code = 1
            return render_template('hospital_reg_init.html', error_code=error_code)
        except:
            print("ERROR!!!!")
            error_code = 2
            return render_template('hospital_reg_init.html', error_code=error_code)
    return render_template('hospital_reg_init.html', error_code=error_code)


@app.route('/hospRegisterUpdate', methods=['GET', 'POST'])
def register_page_update():
    if request.method == 'POST':
        hosp_ID = session["hosp_ID"]
        hospDetails = request.form
        hospName = hospDetails['hospName']
        hospEmail = hospDetails['hospEmail']
        hospAddress = hospDetails['hospAddress']
        hosp_city=hospDetails['hosp_city']
        hosp_state=hospDetails['hosp_state']
        hosp_description=hospDetails['hosp_description']

        if len(hospName) >= 1:
            hospName = hospDetails['hospName']
            update_query = "UPDATE Hospital SET hospName='%s' WHERE hosp_ID='%s'" % (hospName, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        if len(hospEmail) >= 1:
            update_query = "UPDATE Hospital SET hospEmail='%s' WHERE hosp_ID='%s'" % (hospEmail, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()

        try:
            hospPhone = hospDetails['hospPhone']
            update_query = "UPDATE Hospital SET hospPhone='%s' WHERE hosp_ID='%s'" % (hospPhone, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            print("No Phone")

        if len(hospAddress) >= 1:
            update_query = "UPDATE Hospital SET hospAddress='%s' WHERE hosp_ID='%s'" % (hospAddress, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        if len(hosp_city) >= 1:
            update_query = "UPDATE Hospital SET hosp_city='%s' WHERE hosp_ID='%s'" % (hosp_city, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()

        update_query = "UPDATE Hospital SET hosp_state='%s' WHERE hosp_ID='%s'" % (hosp_state, hosp_ID)
        cur = myconn.cursor()
        cur.execute(update_query)
        myconn.commit()
        cur.close()

        if len(hosp_description) >= 1:
            update_query = "UPDATE Hospital SET hosp_description='%s' WHERE hosp_ID='%s'" % (hosp_description, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM Hospital WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospDetails = cur.fetchall()

    return render_template('hospital_reg_update.html', hospDetails=hospDetails, hospName=session["hospName"])



@app.route('/hospLogin', methods=['GET', 'POST'])
def login_page():
    error_code = 0
    if request.method == 'POST':
        hospDetails = request.form
        hosp_ID = hospDetails['hospID']
        hospPassword = hospDetails['hospPassword']

        sql_query = "SELECT * FROM Hospital WHERE hosp_ID ='%s' AND hospPassword ='%s'" % (int(hosp_ID), hospPassword)

        cur = myconn.cursor()
        cur.execute(sql_query)
        hospDetails = cur.fetchall()
        i = 0
        for row in hospDetails:
            i = i + 1
        myconn.commit()
        cur.close()

        if i == 1:
            session["hosp_ID"] = hospDetails[0][0]
            session["hospName"] = hospDetails[0][1]
            session['type'] = 'hospital'
            hosp_ID = session["hosp_ID"]
            cur = myconn.cursor()
            cur.execute("SELECT * FROM Hospital WHERE hosp_ID ='%s'" % (int(hosp_ID)))
            hospAllDetails = cur.fetchall()
            return render_template('hospital_after_login.html', hospName=session["hospName"],
                                   hospAllDetails=hospAllDetails)
        else:
            error_code = 1
            return render_template('hospital_login.html', error_code=error_code)
    return render_template('hospital_login.html', error_code=error_code)


@app.route('/hospAfterLogin', methods=['GET', 'POST'])
def hospital_homepage():
    hosp_ID = session["hosp_ID"]
    cur = myconn.cursor()
    cur.execute("SELECT * FROM Hospital WHERE hosp_ID ='%s'" % (int(hosp_ID)))
    hospAllDetails = cur.fetchall()
    return render_template('hospital_after_login.html', hospName=session["hospName"], hospAllDetails=hospAllDetails)


@app.route('/updateVaccine', methods=['GET', 'POST'])
def update_vaccine_details():
    if request.method == 'POST':
        newVaccDetails = request.form
        hosp_ID = session["hosp_ID"]
        try:
            new_v1 = int(newVaccDetails['v1'])
            update_query = "UPDATE VaccineDetails SET v1_quant='%s' WHERE hosp_ID='%s'" % (new_v1, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            new_v1 = -1
        try:
            new_v2 = int(newVaccDetails['v2'])
            update_query = "UPDATE VaccineDetails SET v2_quant='%s' WHERE hosp_ID='%s'" % (new_v2, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            new_v2 = -1
        try:
            new_v3 = int(newVaccDetails['v3'])
            update_query = "UPDATE VaccineDetails SET v3_quant='%s' WHERE hosp_ID='%s'" % (new_v3, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            new_v3 = -1

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM VaccineDetails WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospVaccineDetails = cur.fetchall()

    return render_template('update_vaccine.html', hospVaccineDetails=hospVaccineDetails,
                           hospName=session["hospName"])  # Pass all vaccine details


@app.route('/addVaccine', methods=['GET', 'POST'])
def add_vaccine_details():
    if request.method == 'POST':
        cur = myconn.cursor()
        hosp_ID = session["hosp_ID"]
        cur.execute("INSERT INTO VaccineDetails(hosp_ID,v1_quant,v2_quant,v3_quant) VALUES(%s,%s,%s,%s)",
                    (int(hosp_ID), int(0), int(0), int(0)))
        myconn.commit()
        cur.close()
    return redirect('/updateVaccine')


@app.route('/updateOxygen', methods=['GET', 'POST'])
def update_oxygen_details():
    if request.method == 'POST':
        newOxyDetails = request.form
        hosp_ID = session["hosp_ID"]
        try:
            new_avail = int(newOxyDetails['lit_avail'])
            update_query = "UPDATE OxygenDetails SET litres_available='%s' WHERE hosp_ID='%s'" % (new_avail, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            new_avail = -1
        try:
            new_supply = int(newOxyDetails['hourly_suppl'])
            update_query = "UPDATE OxygenDetails SET supply_per_hour='%s' WHERE hosp_ID='%s'" % (new_supply, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            new_supply = -1
        try:
            new_price = int(newOxyDetails['price_pl'])
            update_query = "UPDATE OxygenDetails SET price_per_litre='%s' WHERE hosp_ID='%s'" % (new_price, hosp_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            new_price = -1

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM OxygenDetails WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospOxygenDetails = cur.fetchall()

    return render_template('update_oxygen.html', hospOxygenDetails=hospOxygenDetails,
                           hospName=session["hospName"])  # Pass all oxygen details


@app.route('/addOxygen', methods=['GET', 'POST'])
def add_oxygen_details():
    if request.method == 'POST':
        cur = myconn.cursor()
        hosp_ID = session["hosp_ID"]
        cur.execute(
            "INSERT INTO OxygenDetails(hosp_ID,litres_available,supply_per_hour,price_per_litre) VALUES(%s,%s,%s,%s)",
            (int(hosp_ID), int(0), int(0), int(0)))
        myconn.commit()
        cur.close()
    return redirect('/updateOxygen')


@app.route('/updateSurgery', methods=['GET', 'POST'])
def update_surgery_details():
    if request.method == 'POST':
        hosp_ID = session["hosp_ID"]
        newSurgeryDetails = request.form
        s1 = s2 = s3 = 0
        try:
            var1 = newSurgeryDetails["heart"]
            s1 = 1
        except:
            s1 = 0
        try:
            var2 = newSurgeryDetails["joint"]
            s2 = 1
        except:
            s2 = 0
        try:
            var3 = newSurgeryDetails["abdominal"]
            s3 = 1
        except:
            s3 = 0

        update_query = "UPDATE SurgeryDetails SET heart='%s',joint='%s',abdominal='%s' WHERE hosp_ID='%s'" % (
            s1, s2, s3, hosp_ID)
        cur = myconn.cursor()
        cur.execute(update_query)
        myconn.commit()
        cur.close()

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM SurgeryDetails WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospSurgeryDetails = cur.fetchall()

    return render_template('update_surgery.html', hospSurgeryDetails=hospSurgeryDetails,
                           hospName=session["hospName"])  # Pass all surgery details


@app.route('/addSurgery', methods=['GET', 'POST'])
def add_surgery_details():
    if request.method == 'POST':
        cur = myconn.cursor()
        hosp_ID = session["hosp_ID"]
        cur.execute("INSERT INTO SurgeryDetails(hosp_ID,heart,joint,abdominal) VALUES(%s,%s,%s,%s)",
                    (int(hosp_ID), int(0), int(0), int(0)))
        myconn.commit()
        cur.close()
    return redirect('/updateSurgery')


@app.route('/updateBeds', methods=['GET', 'POST'])
def update_beds():
    if request.method == 'POST':
        nbeds = request.form['bed']
        hosp_ID = session["hosp_ID"]
        cur = myconn.cursor()
        cur.execute('UPDATE BedsDetails SET BedsQuantity=%s WHERE hosp_id=%s', (nbeds, hosp_ID))
        myconn.commit()
        cur.close()

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM BedsDetails WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospBedsDetails = cur.fetchall()
    return render_template('update_beds.html', hospBedsDetails=hospBedsDetails,
                           hospName=session["hospName"])  # Pass all bed details


@app.route('/addBeds', methods=['GET', 'POST'])
def add_bed_details():
    if request.method == 'POST':
        cur = myconn.cursor()
        hosp_ID = session["hosp_ID"]
        cur.execute("INSERT INTO BedsDetails(hosp_ID,BedsQuantity) VALUES(%s,%s)", (int(hosp_ID), int(0)))
        myconn.commit()
        cur.close()
    return redirect('/updateBeds')


#  cur.execute(
#                 'UPDATE blood SET AP_Quantity=%s, AN_Quantity=%s, BP_Quantity=%s, BN_Quantity=%s, OP_Quantity=%s, ON_Quantity=%s, ABP_Quantity=%s, ABN_Quantity=%s WHERE hosp_id=%s',
#                 (ap, an, bp, bn, op, on, abp, abn, hid))
#             myconn.commit()

@app.route('/updateBlood', methods=['GET', 'POST'])
def update_blood():
    if request.method == 'POST':
        hosp_ID = session["hosp_ID"]
        x = 0
        try:
            cur = myconn.cursor()
            ap = request.form['ap']
            cur.execute('UPDATE BloodDetails SET AP_Quantity=%s WHERE hosp_id=%s', (ap, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            an = request.form['an']
            cur.execute('UPDATE BloodDetails SET AN_Quantity=%s WHERE hosp_id=%s', (an, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            bp = request.form['bp']
            cur.execute('UPDATE BloodDetails SET BP_Quantity=%s WHERE hosp_id=%s', (bp, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            bn = request.form['bn']
            cur.execute('UPDATE BloodDetails SET BN_Quantity=%s WHERE hosp_id=%s', (bn, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            abp = request.form['abp']
            cur.execute('UPDATE BloodDetails SET ABP_Quantity=%s WHERE hosp_id=%s', (abp, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            abn = request.form['abn']
            cur.execute('UPDATE BloodDetails SET ABN_Quantity=%s WHERE hosp_id=%s', (abn, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            op = request.form['op']
            cur.execute('UPDATE BloodDetails SET OP_Quantity=%s WHERE hosp_id=%s', (op, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        try:
            cur = myconn.cursor()
            on = request.form['on']
            cur.execute('UPDATE BloodDetails SET ON_Quantity=%s WHERE hosp_id=%s', (on, hosp_ID))
            myconn.commit()
            cur.close()
        except Exception as e:
            print(e)
            x = 1
        cur.close()

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM BloodDetails WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospBloodDetails = cur.fetchall()
    return render_template('update_blood.html', hospBloodDetails=hospBloodDetails,
                           hospName=session["hospName"])  # Pass all bed details


@app.route('/addBlood', methods=['GET', 'POST'])
def add_blood_details():
    if request.method == 'POST':
        cur = myconn.cursor()
        hosp_ID = session["hosp_ID"]
        cur.execute(
            'INSERT INTO  BloodDetails(hosp_id,AP_Quantity,AN_Quantity,BP_Quantity,BN_Quantity,OP_Quantity,ON_Quantity,ABP_Quantity,ABN_Quantity) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (int(hosp_ID), int(0), int(0), int(0), int(0), int(0), int(0), int(0), int(0)))
        myconn.commit()
        cur.close()
        return redirect('/updateBlood')


@app.route('/updateAmbulance', methods=['GET', 'POST'])
def update_ambulance():
    if request.method == 'POST':
        try:
            namb = request.form['amb']
            cur = myconn.cursor()
            hosp_ID = session["hosp_ID"]
            cur = myconn.cursor()
            cur.execute('UPDATE AmbulanceDetails SET AmbulanceQuantity=%s WHERE hosp_id=%s', (namb, hosp_ID))
            myconn.commit()
            cur.close()
        except:
            print("Ambulance Error")

    hosp_ID = session["hosp_ID"]
    sql_query = "SELECT * FROM AmbulanceDetails WHERE hosp_ID ='%s'" % (int(hosp_ID))
    cur = myconn.cursor()
    cur.execute(sql_query)
    hospAmbulanceDetails = cur.fetchall()
    if (len(hospAmbulanceDetails)) == 0:
        return redirect('/addAmbulance')
    return render_template('update_ambulance.html', hospAmbulanceDetails=hospAmbulanceDetails,
                           hospName=session["hospName"])  # Pass all bed details


@app.route('/addAmbulance', methods=['GET', 'POST'])
def add_ambulance():
    hosp_ID = session["hosp_ID"]
    cur = myconn.cursor()
    cur.execute('INSERT INTO AmbulanceDetails(hosp_id,AmbulanceQuantity) VALUES(%s,%s)', (hosp_ID, int(0)))
    myconn.commit()
    cur.close()
    return redirect('/updateAmbulance')


@app.route('/doctor_reg', methods=['GET', 'POST'])
def doctor_reg():
    error_code = 0
    if request.method == 'POST':
        docDetails = request.form
        docName = docDetails['docName']
        doc_ID = docDetails['doc_ID']
        docPassword = docDetails['docPassword']
        docPasswordRepeat = docDetails['docPasswordRepeat']

        if docPassword != docPasswordRepeat:
            error_code = 3
            return render_template('doctor_reg.html', error_code=error_code)

        cur = myconn.cursor()
        try:
            print('kk')
            cur.execute("INSERT INTO doctor (doc_ID,docName,docPassword) VALUES(%s,%s,%s)",
                        (doc_ID, docName, docPassword))
            myconn.commit()
            cur.close()
            error_code = 1
            return render_template('doctor_reg.html', error_code=error_code)
        except:
            print("ERROR!!!!")
            error_code = 2
            return render_template('doctor_reg.html', error_code=error_code)
    return render_template('doctor_reg.html', error_code=error_code)


@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    error_code = 0
    if request.method == 'POST':
        docDetails = request.form
        doc_ID = docDetails['doc_ID']
        docPassword = docDetails['docPassword']

        sql_query = "SELECT * FROM doctor WHERE doc_ID ='%s' AND docPassword ='%s'" % (doc_ID, docPassword)

        cur = myconn.cursor()
        cur.execute(sql_query)
        docDetails = cur.fetchall()
        i = 0
        for row in docDetails:
            i = i + 1
        myconn.commit()
        cur.close()

        if i == 1:
            session["doc_ID"] = docDetails[0][0]
            session["docName"] = docDetails[0][1]
            session['sender_id'] = docDetails[0][0]
            session['type'] = 'doctor'
            doc_ID = session["doc_ID"]
            cur = myconn.cursor()
            cur.execute("SELECT * FROM doctor WHERE doc_ID ='%s'" % (doc_ID))
            docAllDetails = cur.fetchall()
            myconn.commit()
            cur.close()

            query = '''SELECT UserID FROM user where UserID IN
            (SELECT Sender_ID FROM chat WHERE Receiver_ID ='%s')
            ''' % (session["doc_ID"])
            cur = myconn.cursor()
            cur.execute(query)
            session["user_senders"] = cur.fetchall()
            myconn.commit()
            cur.close()

            return render_template('doctor_after_login.html', docName=session["docName"],
                                   docAllDetails=docAllDetails)



        else:
            error_code = 1
            return render_template('doctor_login.html', error_code=error_code)
    return render_template('doctor_login.html', error_code=error_code)


@app.route('/doctor_after_login', methods=['GET', 'POST'])
def doctor_after_login():
    doc_ID = session["doc_ID"]
    cur = myconn.cursor()
    cur.execute("SELECT * FROM doctor WHERE doc_ID ='%s'" % (doc_ID))
    docAllDetails = cur.fetchall()
    return render_template('doctor_after_login.html', docName=session["docName"],
                           docAllDetails=docAllDetails)


@app.route('/update_doctors', methods=['GET', 'POST'])
def update_doctors():
    if request.method == 'POST':
        doc_ID = session["doc_ID"]
        docDetails = request.form
        docName = docDetails['docName']
        doc_s = docDetails['doc_s']
        docAddress = docDetails['docAddress']
        hosp_id = docDetails['hosp_id']
        if len(docName) >= 1:
            docName = docDetails['docName']
            update_query = "UPDATE doctor SET docName='%s' WHERE doc_ID='%s'" % (docName, doc_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        if len(doc_s) >= 1:
            update_query = "UPDATE doctor SET doc_s='%s' WHERE doc_ID='%s'" % (doc_s, doc_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()

        try:
            docPhone = docDetails['docPhone']
            update_query = "UPDATE doctor SET docPhone='%s' WHERE doc_ID='%s'" % (docPhone, doc_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            print("No Phone")

        if len(docAddress) >= 1:
            update_query = "UPDATE doctor SET docAddress='%s' WHERE doc_ID='%s'" % (docAddress, doc_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()

        try:
            hosp_id = docDetails['hosp_id']
            update_query = "UPDATE doctor SET hosp_id='%s' WHERE doc_ID='%s'" % (hosp_id, doc_ID)
            cur = myconn.cursor()
            cur.execute(update_query)
            myconn.commit()
            cur.close()
        except:
            print("No Hospital")

    doc_ID = session["doc_ID"]
    sql_query = "SELECT * FROM doctor WHERE doc_ID ='%s'" % (doc_ID)
    cur = myconn.cursor()
    cur.execute(sql_query)
    docDetails = cur.fetchall()

    return render_template('update_doctors.html', docDetails=docDetails, docName=session["docName"])


@app.route('/user')
def home():
    return render_template('user_home.html', error_code=0)

@app.route('/user_index', methods=['GET', 'POST'])
def user_index():
    cur = myconn.cursor()
    cur.execute('SELECT * FROM user WHERE UserID=%s'%(session['UserId']))
    user_details = cur.fetchall()
    myconn.commit()
    cur.close()
    return render_template('user_index.html',user_details=user_details)



@app.route('/user_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        passwd = request.form['passwd']
        cur = myconn.cursor()
        cur.execute('SELECT * FROM user WHERE UserId=%s AND UserPassword=%s', (userid, passwd))
        acc = cur.fetchone()
        myconn.commit()
        cur.close()
        if acc:
            session['loggedin'] = True
            session['UserId'] = userid
            session['Name'] = acc[1]
            session['Address'] = acc[3]
            session['Phone'] = acc[4]
            session['DOB'] = acc[5]
            session['sender_id'] = userid
            session['type'] = 'user'
            session['search_state'] = 'None Selected'
            return redirect('/user_index')
        else:
            return render_template('user_home.html', error_code=2)


@app.route('/user_register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            userid = request.form['userid']
            name = request.form['name']
            passwd = request.form['passwd']
            cpasswd = request.form['cpasswd']
            if passwd != cpasswd:
                return render_template('user_home.html', error_code=3)

            cur = myconn.cursor()
            cur.execute('INSERT INTO user (UserId, UserName, UserPassword) VALUES (%s, %s, %s)', (userid, name, passwd))
            myconn.commit()
            cur.close()
            return render_template('user_home.html', error_code=1)
        except:
            return render_template('user_home.html', error_code=2)

@app.route('/user_update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        add = request.form['add']
        phno = request.form['phno']
        dob = request.form['dob']

        print(add,phno,dob)

        if add!='':
            cur = myconn.cursor()
            cur.execute('UPDATE user SET UserAddress=%s WHERE UserId=%s',(add,session['UserId']))
            myconn.commit()
            cur.close()
        else:
            print('No Address')

        if phno:
            cur = myconn.cursor()
            cur.execute('UPDATE user SET  UserPhone=%s WHERE UserId=%s',(phno,session['UserId']))
            myconn.commit()
            cur.close()
            session['Phone'] = phno
        else:
            print('No Phone')

        try:
            if dob:
                cur = myconn.cursor()
                cur.execute('UPDATE user SET UserDOB=%s WHERE UserId=%s',(dob,session['UserId']))
                myconn.commit()
                cur.close()
                
        except:
            print('No DOB')
        
        return redirect('/user_index')


@app.route('/user_logout')
def logout():
    session.pop('loggedin', None)
    session.pop('UserId', None)
    session.pop('Name', None)
    session.pop('Address', None)
    session.pop('Phone', None)
    session.pop('DOB', None)
    return render_template('home.html', polarity=5.0, subjectivity=5.0)

@app.route('/addTimeSlot', methods=['GET', 'POST']) 
def addTimeSlot():
    doc_ID = session["doc_ID"]
    if request.method == 'POST':
        startTime = request.form['startTime']
        endTime = request.form['endTime']
        date = request.form['date']
        query = "INSERT INTO TimeSlots (Doc_ID,Start_Time,End_Time,Appt_Date,Availability) VALUES ('%s','%s','%s','%s',%s)"%(doc_ID,startTime,endTime,date,1)
        cur = myconn.cursor()
        cur.execute(query)
        myconn.commit()
        cur.close()
        print("Add Time Slot")

    return render_template('add_time_slot.html')


@app.route('/show_appointments/<string:doc_ID>', methods=['GET', 'POST'])  # On User's Side
def show_appointments(doc_ID):
    if request.method == 'POST':
        session["preDesc"]= request.form['preDesc']

    today_details = tomorrow_details = dafter_details = []
    session['appointment_search_docID'] = doc_ID
    today = (datetime.datetime.today()).strftime("%Y-%m-%d")
    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    dayafter = (datetime.datetime.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

    query = "SELECT * FROM TimeSlots WHERE doc_ID='%s' and Appt_Date='%s' and Availability=%s" % (doc_ID, today, 1)
    cur = myconn.cursor()
    cur.execute(query)
    today_details = cur.fetchall()
    myconn.commit()

    query = "SELECT * FROM TimeSlots WHERE doc_ID='%s' and Appt_Date='%s' and Availability=%s" % (doc_ID, tomorrow, 1)
    cur = myconn.cursor()
    cur.execute(query)
    tomorrow_details = cur.fetchall()
    myconn.commit()

    query = "SELECT * FROM TimeSlots WHERE doc_ID='%s' and Appt_Date='%s' and Availability=%s" % (doc_ID, dayafter, 1)
    cur = myconn.cursor()
    cur.execute(query)
    dafter_details = cur.fetchall()
    myconn.commit()

    return render_template('show_appointments.html', today_details=today_details, tomorrow_details=tomorrow_details,
                           dafter_details=dafter_details, error_code=-1)

    
# Acceptance_Status = 0 ... Request has been sent and is pending
# Acceptance Status = 1 ... Request has been accepted
# Acceptance Status = 2 ... Request has been declined
# Acceptance Status = 3 ... Request has been cancelled




@app.route('/request_appointment/<int:Time_ID>', methods=['GET', 'POST'])  # On User's Side
def request_appointment(Time_ID):
    UserID = session['UserId']
    Time_ID = Time_ID
    query = "SELECT DISTINCT Doc_ID FROM TimeSlots where Time_ID=%s" % (Time_ID)
    cur = myconn.cursor()
    cur.execute(query)
    Doc_ID = (cur.fetchone())[0]
    try:
        query = '''INSERT INTO Appointment (UserID,Time_ID,doc_ID,MeetLink,PreDescription,PostDescription,Acceptance_Status)
        VALUES (%s, %s, '%s','%s','%s','%s',%s)
         ''' % (UserID, Time_ID, Doc_ID, 'www.googlemeet.com', session['preDesc'], '', 0)
        cur.execute(query)
        myconn.commit()
        error_code = 0
    except:
        error_code = 1

    doc_ID = session['appointment_search_docID']
    today = (datetime.datetime.today()).strftime("%Y-%m-%d")
    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    dayafter = (datetime.datetime.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

    query = "SELECT * FROM TimeSlots WHERE doc_ID='%s' and Appt_Date='%s' and Availability=%s" % (doc_ID, today, 1)
    cur = myconn.cursor()
    cur.execute(query)
    today_details = cur.fetchall()
    myconn.commit()

    query = "SELECT * FROM TimeSlots WHERE doc_ID='%s' and Appt_Date='%s' and Availability=%s" % (doc_ID, tomorrow, 1)
    cur = myconn.cursor()
    cur.execute(query)
    tomorrow_details = cur.fetchall()
    myconn.commit()

    query = "SELECT * FROM TimeSlots WHERE doc_ID='%s' and Appt_Date='%s' and Availability=%s" % (doc_ID, dayafter, 1)
    cur = myconn.cursor()
    cur.execute(query)
    dafter_details = cur.fetchall()
    myconn.commit()

    return render_template('show_appointments.html', today_details=today_details, tomorrow_details=tomorrow_details,
                           dafter_details=dafter_details, error_code=error_code)


@app.route('/view_appointments', methods=['GET', 'POST'])  # On Doctor's Side
def view_appointments():
    Doc_ID = session['doc_ID']
    today = (datetime.datetime.today()).strftime("%Y-%m-%d")
    query = '''
        SELECT apt.UserID,apt.doc_ID,apt.MeetLink,apt.PreDescription,apt.PostDescription,apt.Acceptance_Status,
               tslots.Start_Time,tslots.End_Time,tslots.Appt_Date,
               user.UserName , user.UserPhone,
               apt.Time_ID
        FROM Appointment apt 
        JOIN TimeSlots tslots on apt.Time_ID = tslots.Time_ID
        JOIN user user on apt.UserID = user.UserID
        WHERE apt.doc_ID='%s' AND (apt.Acceptance_Status=%s OR apt.Acceptance_Status=%s)
        and tslots.Appt_Date >= '%s'
        ORDER BY tslots.Appt_Date ASC''' % (Doc_ID, 0, 1, today)

    # Acceptance_Status = 0 ... Request has been sent and is pending
    # Acceptance Status = 1 ... Request has been accepted
    # Acceptance Status = 2 ... Request has been declined
    # Acceptance Status = 3 ... Request has been cancelled

    status = {0: 'Request Pending', 1: 'Request Accepted', 2: 'Request Declined', 3: 'Request Cancelled'}
    cur = myconn.cursor()
    cur.execute(query)
    appointments = cur.fetchall()
    print(appointments)
    return render_template('view_appointments.html', appointments=appointments, status=status)


@app.route('/appointment_notifications', methods=['GET', 'POST'])  # On User's Side
def appointment_notifications():
    UserID = session['UserId']
    today = (datetime.datetime.today()).strftime("%Y-%m-%d")
    query = '''
        SELECT apt.UserID,apt.doc_ID,apt.MeetLink,apt.PreDescription,apt.PostDescription,apt.Acceptance_Status,
               tslots.Start_Time,tslots.End_Time,tslots.Appt_Date,
               user.UserName , user.UserPhone,
               apt.Time_ID
        FROM Appointment apt 
        JOIN TimeSlots tslots on apt.Time_ID = tslots.Time_ID
        JOIN user user on apt.UserID = user.UserID
        WHERE apt.UserID='%s' and tslots.Appt_Date >= '%s'
        ORDER BY tslots.Appt_Date ASC''' % (UserID, today)

    # Acceptance_Status = 0 ... Request has been sent and is pending
    # Acceptance Status = 1 ... Request has been accepted
    # Acceptance Status = 2 ... Request has been declined
    # Acceptance Status = 3 ... Request has been cancelled

    status = {0: 'Request Pending', 1: 'Request Accepted', 2: 'Request Declined', 3: 'Request Cancelled'}
    cur = myconn.cursor()
    cur.execute(query)
    appointments = cur.fetchall()
    print(appointments)
    return render_template('appointment_notifications.html', appointments=appointments, status=status)

@app.route('/appointment_history', methods=['GET', 'POST'])
def appointment_history():
    user_type=session['type']

    if user_type == 'doctor':
        Doc_ID = session['doc_ID']
        today = (datetime.datetime.today()).strftime("%Y-%m-%d")
        query = '''
            SELECT apt.UserID,apt.doc_ID,apt.MeetLink,apt.PreDescription,apt.PostDescription,apt.Acceptance_Status,
                tslots.Start_Time,tslots.End_Time,tslots.Appt_Date,
                user.UserName , user.UserPhone,
                apt.Time_ID
            FROM Appointment apt 
            JOIN TimeSlots tslots on apt.Time_ID = tslots.Time_ID
            JOIN user user on apt.UserID = user.UserID
            WHERE apt.doc_ID='%s' AND apt.Acceptance_Status=%s
            and tslots.Appt_Date < '%s'
            ORDER BY tslots.Appt_Date ASC''' % (Doc_ID, 1, today)

    if user_type == 'user':
        UserID = session['UserId']
        today = (datetime.datetime.today()).strftime("%Y-%m-%d")
        query = '''
            SELECT apt.UserID,apt.doc_ID,apt.MeetLink,apt.PreDescription,apt.PostDescription,apt.Acceptance_Status,
                tslots.Start_Time,tslots.End_Time,tslots.Appt_Date,
                user.UserName , user.UserPhone,
                apt.Time_ID
            FROM Appointment apt 
            JOIN TimeSlots tslots on apt.Time_ID = tslots.Time_ID
            JOIN user user on apt.UserID = user.UserID
            WHERE apt.UserID='%s' AND apt.Acceptance_Status=%s
            and tslots.Appt_Date < '%s'
            ORDER BY tslots.Appt_Date ASC''' % (UserID, 1,  today)

    cur = myconn.cursor()
    cur.execute(query)
    pastAppointments = cur.fetchall()
    myconn.commit()
    cur.close()

    return render_template('appointment_history.html',user_type=user_type,pastAppointments=pastAppointments)

@app.route('/updatePostDesc/<int:Time_ID>/<int:UserID>', methods=['GET', 'POST'])
def updatePostDesc(Time_ID,UserID):
    if request.method == 'POST':
        postDesc = request.form['postDesc']
        query = '''
        UPDATE Appointment SET PostDescription='%s' WHERE 
        Time_ID=%s AND UserID=%s
        '''%(postDesc,Time_ID,UserID)

        cur = myconn.cursor()
        cur.execute(query)
        myconn.commit()
        cur.close()
    return redirect('/appointment_history')



@app.route('/appointment_action/<int:Time_ID>/<int:UserID>/<string:action>', methods=['GET', 'POST'])
def appointment_action(Time_ID, UserID, action):
    print(Time_ID, UserID, action)
    if action == 'Accept':
        query = '''UPDATE Appointment SET Acceptance_Status=%s WHERE Time_ID=%s AND UserID=%s''' % (1, Time_ID, UserID)
    elif action == 'Reject':
        query = "UPDATE Appointment SET Acceptance_Status=%s WHERE Time_ID=%s AND UserID=%s" % (2, Time_ID, UserID)
    elif action == 'Cancel':
        query = "UPDATE Appointment SET Acceptance_Status=%s WHERE Time_ID=%s AND UserID=%s" % (3, Time_ID, UserID)
    elif action == 'Dismiss':
        query = "DELETE FROM Appointment WHERE Time_ID=%s AND UserID=%s" % (Time_ID, UserID)
        cur = myconn.cursor()
        cur.execute(query)
        myconn.commit()
        cur.close()
        return redirect('/appointment_notifications')

    cur = myconn.cursor()
    cur.execute(query)
    myconn.commit()
    cur.close()

    make_available = "UPDATE TimeSlots SET Availability=%s WHERE Time_ID=%s" % (1, Time_ID)
    cur = myconn.cursor()
    cur.execute(make_available)
    myconn.commit()
    cur.close()

    change_availability = '''UPDATE TimeSlots SET Availability=%s
    WHERE EXISTS (SELECT * FROM Appointment WHERE Time_ID=%s AND Acceptance_Status=%s)
    AND Time_ID = %s''' % (0, Time_ID, 1, Time_ID)
    cur = myconn.cursor()
    cur.execute(change_availability)
    myconn.commit()
    cur.close()

    status1 = "SELECT * FROM Appointment WHERE Time_ID=%s AND Acceptance_Status=%s" % (Time_ID, 1)

    cur = myconn.cursor()
    cur.execute(status1)
    confirmed = cur.fetchall()
    i = 0
    for row in confirmed:
        i = i + 1

    if i > 0:
        change_status = '''UPDATE Appointment SET Acceptance_Status = %s
        WHERE Acceptance_Status = %s
        AND Time_ID=%s''' % (2, 0, Time_ID)
        cur = myconn.cursor()
        cur.execute(change_status)
        myconn.commit()
        cur.close()

    return redirect('/view_appointments')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    acc = []
    if request.method == 'POST':
        sender = session['sender_id']
        receiver = session['receiver_id']
        msg = request.form['msg']
        cur = myconn.cursor()
        cur.execute('INSERT INTO chat VALUES (CURTIME(), %s, %s, %s, CURDATE())', (sender, receiver, msg))
        myconn.commit()
        cur.close()

        cur1 = myconn.cursor()
        cur1.execute('SELECT * FROM chat WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s)',
                     (sender, receiver, receiver, sender))
        acc = cur1.fetchall()
        myconn.commit()
        cur1.close()

    return render_template('chat_page.html', acc=acc, user_type=session['type'])


@app.route('/chat_with/<string:receiver_id>', methods=['GET', 'POST'])
def chat_with(receiver_id):
    print(receiver_id)
    if receiver_id != 'doctorid':
        session['receiver_id'] = receiver_id
        sender = session['sender_id']
        receiver = session['receiver_id']
        print(sender, receiver)

        cur1 = myconn.cursor()
        cur1.execute(
            "SELECT * FROM chat WHERE (sender_id='%s' AND receiver_id='%s') OR (sender_id='%s' AND receiver_id='%s')" % (
            sender, receiver, receiver, sender))
        acc = cur1.fetchall()
        print(acc)
        myconn.commit()
        cur1.close()
        return render_template('chat_page.html', acc=acc, user_type=session['type'])

    if request.method == 'POST':
        session['receiver_id'] = request.form['select']
        sender = session['sender_id']
        receiver = session['receiver_id']

        cur1 = myconn.cursor()
        cur1.execute(
            "SELECT * FROM chat WHERE (sender_id='%s' AND receiver_id='%s') OR (sender_id='%s' AND receiver_id='%s')" % (
            sender, receiver, receiver, sender))
        acc = cur1.fetchall()
        myconn.commit()
        cur1.close()
        return render_template('chat_page.html', acc=acc, user_type=session['type'])

    return render_template('chat_page.html', user_type=session['type'])


@app.route('/add_vaccine_slot', methods=['GET', 'POST'])
def add_vaccine_slot():
    days = []
    ls = []
    msg = ""
    if request.method == 'POST':
        cur = myconn.cursor()
        hosp_id = session['hosp_ID']
        appt_date = request.form.get('appt_date')
        dose = request.form.get('dose')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        vaccine = request.form.getlist('vaccine')
        total_persons = request.form.get('total_persons')
        print(vaccine)
        for vac in vaccine:
            cur.execute(
                'SELECT * FROM vaccine_slots WHERE hosp_id = %s AND start_time = %s AND end_time = %s AND appt_date = %s AND dose = %s AND vaccine_type = %s',
                (hosp_id, start_time, end_time, appt_date, dose, vac,))
            query_present = cur.fetchone()
            if query_present != None:
                msg = "Slot is already present"
                return render_template('vaccine_portal.html', msg=msg, ls=ls, days=days)
        for vac in vaccine:
            cur.execute(
                'INSERT INTO vaccine_slots(hosp_id, start_time, end_time, appt_date, dose, total_persons, vaccine_type) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (int(hosp_id), start_time, end_time, appt_date, int(dose), total_persons, vac,))
            myconn.commit()
        msg = "Added Sucessfully!!"

    return render_template('vaccine_portal.html', msg=msg, ls=ls, days=days)


@app.route('/display_vaccine_bookings', methods=['GET', 'POST'])
def display_vaccine_bookings():
    days = []
    ls = []
    msg = ""
    if (request.method == 'POST'):
        cur = myconn.cursor()
        days = request.form.getlist('day')
        hosp_id = session['hosp_ID']
        days_dict = {}
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = tomorrow + timedelta(days=1)
        today = today.strftime('%Y-%m-%d')
        tomorrow = tomorrow.strftime('%Y-%m-%d')
        day_after_tomorrow = day_after_tomorrow.strftime('%Y-%m-%d')
        for t in days:
            if (t == 'today'):
                days_dict[t] = today
            elif (t == 'tomorrow'):
                days_dict[t] = tomorrow
            else:
                days_dict[t] = day_after_tomorrow
        ls = []
        for t in days:
            query = '''
                    SELECT vaccine_book.UserID, 
                            user.UserName, 
                            user.UserPhone, 
                            vaccine_slots.start_time, 
                            vaccine_slots.end_time, 
                            vaccine_slots.appt_date, 
                            vaccine_slots.dose, 
                            vaccine_slots.vaccine_type
                    FROM vaccine_book
                    JOIN user 
                        ON vaccine_book.UserID = user.UserID
                    JOIN vaccine_slots
                        ON vaccine_book.vaccine_time_id = vaccine_slots.vaccine_time_id
                    WHERE vaccine_book.hosp_id = %s AND appt_date = %s'''

            cur.execute(query, (hosp_id, days_dict[t],))
            res = cur.fetchall()
            ls.append(res)

    return render_template('vaccine_portal.html', msg=msg, ls=ls, days=days)


@app.route('/search_blood/<int:hosp_id>', methods=['GET', 'POST'])
def search_blood(hosp_id):
    hospBloodDetails = ''
    query = "SELECT * FROM BloodDetails WHERE hosp_ID ='%s'" % (hosp_id)
    cur = myconn.cursor()
    cur.execute(query)
    hospBloodDetails = cur.fetchall()
    return render_template('search_blood.html', hospBloodDetails=hospBloodDetails)

@app.route('/search_oxygen/<int:hosp_id>', methods=['GET', 'POST'])
def search_oxygen(hosp_id):
    hospOxygenDetails = ''
    query = "SELECT * FROM OxygenDetails WHERE hosp_ID ='%s'" % (hosp_id)
    cur = myconn.cursor()
    cur.execute(query)
    hospOxygenDetails = cur.fetchall()
    return render_template('search_oxygen.html', hospOxygenDetails=hospOxygenDetails)


@app.route('/search_beds/<int:hosp_id>', methods=['GET', 'POST'])
def search_beds(hosp_id):
    hospBedsDetails = ''
    query = "SELECT * FROM BedsDetails WHERE hosp_ID ='%s'" % (hosp_id)
    cur = myconn.cursor()
    cur.execute(query)
    hospBedsDetails = cur.fetchall()
    return render_template('search_beds.html', hospBedsDetails=hospBedsDetails)


@app.route('/search_surgery/<int:hosp_id>', methods=['GET', 'POST'])
def search_surgery(hosp_id):
    hospSurgeryDetails = ''
    query = "SELECT * FROM SurgeryDetails WHERE hosp_ID ='%s'" % (hosp_id)
    cur = myconn.cursor()
    cur.execute(query)
    hospSurgeryDetails = cur.fetchall()
    return render_template('search_surgery.html',hospSurgeryDetails=hospSurgeryDetails)


@app.route('/search_ambulance/<int:hosp_id>', methods=['GET', 'POST'])
def search_ambulance(hosp_id):
    hospAmbulanceDetails = ''
    query = "SELECT * FROM AmbulanceDetails WHERE hosp_ID ='%s'" % (hosp_id)
    cur = myconn.cursor()
    cur.execute(query)
    hospAmbulanceDetails = cur.fetchall()
    return render_template('search_ambulance.html', hospAmbulanceDetails=hospAmbulanceDetails)


@app.route('/vaccine_book/<int:hosp_id>', methods=['GET', 'POST'])
def vaccine_book(hosp_id):
    p=0
    user = session['UserId']
    error = 0
    if hosp_id==0:
        return 'Error'
    session['helper_hosp']=hosp_id
    hospvaccineDetails = ''
    if request.method == 'POST':
        dose = request.form['dose']
        vaccine_type = request.form['type']

        if dose=='1':
            query = '''select vs.appt_date, vs.vaccine_type
                        from vaccine_book vb join vaccine_slots vs on vs.vaccine_time_id=vb.vaccine_time_id
                        where vb.dose='%s' and vb.UserID='%s' ''' % (1, user)
            cur = myconn.cursor()
            cur.execute(query)
            m = cur.fetchall()
            cur.close()
            if m!=[]:
                return render_template('vaccine_book.html', hospvaccineDetails=hospvaccineDetails,hosp_id=hosp_id,error=5)
            
            query = "SELECT * FROM vaccine_slots WHERE hosp_ID ='%s' and dose='%s' and vaccine_type='%s' and appt_date>='%s' and total_persons>%s" % (hosp_id, dose, vaccine_type,datetime.date.today(),0)
            cur = myconn.cursor()
            cur.execute(query)
            hospvaccineDetails = cur.fetchall()
            return render_template('vaccine_book.html', hospvaccineDetails=hospvaccineDetails,hosp_id=hosp_id,error=error,p=1)
        
        else:
            query = '''select vs.appt_date, vs.vaccine_type
                        from vaccine_book vb join vaccine_slots vs on vs.vaccine_time_id=vb.vaccine_time_id
                        where vb.dose='%s' and vb.UserID='%s' ''' % (1, user)
            cur = myconn.cursor()
            cur.execute(query)
            m = cur.fetchall()
            cur.close()
            if m!=[]:
                print(m)
                today = (datetime.datetime.today()).strftime("%Y-%m-%d")
                x=(m[0][0]).strftime("%Y-%m-%d")
                a = arrow.get(today)
                b = arrow.get(x)
                delta = (a - b).days
                if m[0][1]!=vaccine_type:
                    return render_template('vaccine_book.html', hospvaccineDetails=hospvaccineDetails,hosp_id=hosp_id,error=4)
                if (m[0][1]=='covishield' and delta<84) or (m[0][1]=='covaxin' and delta<28) or (m[0][1]=='sputnik' and delta<21):
                    return render_template('vaccine_book.html', hospvaccineDetails=hospvaccineDetails,hosp_id=hosp_id,error=1)
               
                
            query = "SELECT * FROM vaccine_slots WHERE hosp_ID ='%s' and dose='%s' and vaccine_type='%s' and appt_date>='%s' and total_persons>%s" % (hosp_id, dose, vaccine_type, datetime.date.today(),0)
            cur = myconn.cursor()
            cur.execute(query)
            hospvaccineDetails = cur.fetchall()
            return render_template('vaccine_book.html', hospvaccineDetails=hospvaccineDetails, hosp_id=hosp_id,error=error,p=1)

    return render_template('vaccine_book.html', hospvaccineDetails=hospvaccineDetails, hosp_id=hosp_id, error=error)


@app.route('/book', methods=['GET', 'POST'])
def book():
    error=0
    h=session['helper_hosp']
    hosp_id=int(h)
    if request.method == 'POST':
        time_id = request.form['time_id']
        query = "SELECT * FROM vaccine_slots WHERE vaccine_time_id='%s'" % (time_id)
        cur = myconn.cursor()
        cur.execute(query)
        hospvaccinedetails = cur.fetchall()
        cur.close()
        user = session['UserId']
        m=int(hospvaccinedetails[0][6])

        concurrent_book_query = "SELECT total_persons FROM vaccine_slots WHERE vaccine_time_id='%s'" % (time_id)
        cur = myconn.cursor()
        cur.execute(concurrent_book_query)
        slots = cur.fetchall()
        left_slots = slots[0][0]
        if left_slots==0:
            return render_template('vaccine_book.html',error=6,hosp_id=hosp_id)

        try:
            query = "INSERT INTO vaccine_book(UserID,vaccine_time_id,hosp_id,dose) VALUES ('%s',%s,%s,%s)" % (
            user, int(hospvaccinedetails[0][0]), int(hospvaccinedetails[0][1]), int(hospvaccinedetails[0][5]))
            cur = myconn.cursor()
            cur.execute(query)
            myconn.commit()
            query = "update vaccine_slots set total_persons=%s WHERE vaccine_time_id='%s'" % (int(m-1),time_id)
            cur = myconn.cursor()
            cur.execute(query)
            myconn.commit()
            cur.close()

            return render_template('vaccine_book.html',error=3,hosp_id=hosp_id)

        except:
            
            return render_template('vaccine_book.html',error=2,hosp_id=hosp_id)

    return render_template('vaccine_book.html')


@app.route('/search_doctors/<string:speciality>', methods=['GET', 'POST'])
def search_doctors(speciality):
    session['srch_doc_speciality'] = speciality
    session["preDesc"]="None"

    specialities = ['Physician', 'Dentist', 'Obstetrician', 'Opthalmologist', 'ENT','Cardiologist', 'Psychiatrist',
                    'Homeopath', 'Ayurveda']

    if session['srch_doc_speciality'] == 'none':
        return render_template('search_doctors.html', check=False, specialities=specialities)
    else:
        doc_s = session['srch_doc_speciality']
        cur = myconn.cursor()
        cur.execute("SELECT * FROM doctor WHERE doc_s='%s' " % (doc_s))
        srch_doctors = cur.fetchall()
        myconn.commit()
        cur.close()
        print(srch_doctors)
        return render_template('search_doctors.html', check=True, srch_doctors=srch_doctors, specialities=specialities,
                               doc_s=doc_s)



@app.route('/select_state', methods=['GET', 'POST'])
def select_state():
    all_hospital = []
    all_cities=''
    session['search_state'] = 'None'
    session['search_city'] = 'None'

    if request.method == 'POST':
        s = request.form['state']
        session['search_state'] = s
        
    query = "SELECT DISTINCT hosp_city FROM Hospital where hosp_state='%s'"%(session['search_state'])
    cur = myconn.cursor()
    cur.execute(query)
    all_cities = cur.fetchall()
        
    return render_template('location.html', all_cities=all_cities, all_hospital=all_hospital)

@app.route('/select_city', methods=['GET', 'POST'])
def select_city():
    all_hospital=[]
    if request.method == 'POST':
        try:
            city = request.form['city']
            if city=='all':
                session['search_city'] = "All"
            else:
                session['search_city'] = city

            
            if session['search_city']=='All':
                query = "SELECT * FROM Hospital WHERE hosp_state='%s'"%(session['search_state'])
            else:
                query = "SELECT * FROM Hospital WHERE hosp_state='%s' AND hosp_city='%s'"%(session['search_state'],session['search_city'])

            cur = myconn.cursor()
            cur.execute(query)
            all_hospital = cur.fetchall()


        except:
            print("Invalid Query")

       
            
        return render_template('location.html', all_hospital=all_hospital)

@app.route('/mental_health',methods=['GET','POST'])
def mental_health():
    if request.method == 'POST':
        statement = request.form.get('statement')
        result = TextBlob(statement).sentiment
        print(result)
        polarity = float(result.polarity)
        subjectivity = float(result.subjectivity)
        # print(type(polarity))
        return render_template('mental_health.html', polarity=round(polarity, 4), subjectivity=round(subjectivity, 4))

    return render_template('mental_health.html', polarity=5.0, subjectivity=5.0)


@app.route('/vaccine_notifications', methods=['GET', 'POST'])
def vaccine_notifications():
    UserID = session['UserId']

    query = '''
            select vs.appt_date,h.hospName,vs.start_time,vs.end_time,vs.vaccine_type,vs.dose 
            from vaccine_book vb join vaccine_slots vs on vs.vaccine_time_id=vb.vaccine_time_id 
            join Hospital h on h.hosp_id=vs.hosp_id where vb.dose='%s' and vb.UserID='%s' ''' % (1, UserID)
    cur = myconn.cursor()
    cur.execute(query)
    d1 = cur.fetchall()
    cur.close()

    query = '''
                select vs.appt_date,h.hospName,vs.start_time,vs.end_time,vs.vaccine_type,vs.dose 
                from vaccine_book vb join vaccine_slots vs on vs.vaccine_time_id=vb.vaccine_time_id 
                join Hospital h on h.hosp_id=vs.hosp_id where vb.dose='%s' and vb.UserID='%s' ''' % (2, UserID)
    cur = myconn.cursor()
    cur.execute(query)
    d2 = cur.fetchall()
    cur.close()
    print(d2)
    query = '''select UserName from user where UserID='%s' ''' % (UserID)
    cur = myconn.cursor()
    cur.execute(query)
    username = cur.fetchall()
    cur.close()

    return render_template('vaccine_notifications.html',d1=d1,d2=d2,UserID=UserID,username=username)

@app.route('/giveRating/<string:doc_ID>/<string:user_name>/<int:Time_ID>',methods=['GET', 'POST'])
def giveRating(doc_ID,user_name,Time_ID):
    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        
        try:   
            cur = myconn.cursor()
            cur.execute("INSERT INTO Doctor_Reviews (Time_ID,doc_ID,User_Name,Review,Rating) VALUES (%s,%s,%s,%s,%s)",(int(Time_ID),doc_ID,user_name,review,int(rating)))
            myconn.commit()
            cur.close()
        except:
            flash("You Have already given a review!")
        return redirect('/appointment_history')

@app.route('/view_reviews/<string:doc_ID>/<string:doc_name>',methods=['GET', 'POST'])
def viewRatings(doc_ID,doc_name):
    query = "SELECT * FROM Doctor_Reviews WHERE doc_ID='%s'"%(doc_ID)
    cur = myconn.cursor()
    cur.execute(query)
    reviews = cur.fetchall()
    cur.close()
    query = "SELECT AVG(Rating) FROM Doctor_Reviews WHERE doc_ID='%s'" %(doc_ID)
    cur = myconn.cursor()
    cur.execute(query)
    try:
        avg_rating = ((cur.fetchall())[0][0])
    except:
        avg_rating='Unrated'
    cur.close()
    print(reviews)
    return render_template('ratings_and_reviews.html',reviews=reviews,doc_name = doc_name,avg_rating=avg_rating)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
