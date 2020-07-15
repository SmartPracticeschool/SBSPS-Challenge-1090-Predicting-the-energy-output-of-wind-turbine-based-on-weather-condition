from flask import Flask,render_template,request,redirect,url_for,flash
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import datetime
import json
import numpy
import os
import atexit
from Server import *
from Server.WeatherAPI import get_all_Result
from Server.ChartData import get_LineChartData,get_BarChartData


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e29e32df8eb2530cf8d5022cea83e1601eba907caa0a1bec'

port = int(os.getenv('VCAP_APP_PORT', '5000'))

hours_dict = {5: 12,9: 24,13: 36,17: 48,21: 60,25: 72}

myDatabaseDemo = None
client = None

# This is for Cloudant database Connection ...
try:
    if "CLOUDANT_URL" in os.environ:
        admin_user = os.environ['ADMIN_USERNAME']
        admin_password = os.environ['ADMIN_PASSWORD']
        username = os.environ['CLOUDANT_USERNAME']
        password = os.environ['CLOUDANT_PASSWORD']
        url = os.environ['CLOUDANT_URL']
        client = Cloudant(username,password,url=url)
        client.connect()
        myDatabaseDemo = client.create_database(os.environ['DATABASE_NAME'])
    else:
        admin_user = ADMIN_USERNAME
        admin_password = ADMIN_PASSWORD
        username = CLOUDANT_USERNAME
        password = CLOUDANT_PASSWORD
        url = CLOUDANT_URL
        client = Cloudant(username,password,url=url)
        client.connect()
        db_name = DATABASE_NAME
        myDatabaseDemo = client.create_database(db_name)
except:
    pass



# This class is Used to encode from python object to json object when we use : 'json.dumps()' Method ...
#  REFERENCE : https://stackoverflow.com/
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/result', methods=["POST","GET"])
def result():
    if request.method== "POST":
        if 'predict' in request.form:
            hours = int(request.form['hours'])
            redius = float(request.form['redius'])
            efficiency = float(request.form['efficiency'])/100
            result = get_all_Result(redius,efficiency,hours)
            if result != None:
                outputPower = max(result[0])
                indexOutputPower = result[0].index(outputPower)
                datetimeOutputPower = result[2][indexOutputPower]
                dateTimeObj = datetime.datetime.strptime(datetimeOutputPower,'%Y-%m-%d %H:%M:%S')
                Date = str(dateTimeObj.date())
                dayName = dateTimeObj.strftime("%A")
                Time = str(dateTimeObj.time())
                lineChartDataRaw = get_LineChartData(result[2],result[0])
                barChartData = get_BarChartData(result[2],result[1],result[3],result[4])
                lineChartData = json.dumps(lineChartDataRaw,cls=MyEncoder)
                barChartData = json.dumps(barChartData,cls=MyEncoder)
                return render_template('result.html',Date=Date,dayName=dayName,
                                        Time=Time,outputPower=round(outputPower,2),
                                        lineChartData=lineChartData,lineChartDataRaw=lineChartDataRaw,
                                        barChartData=barChartData,hour=hours_dict[hours])
            else:
                return render_template('wrongInput.html')

        elif 'contact' in request.form:
            # This is a trigger message to activate the popup modal .. 
            flash("true")
            user_data = request.form.to_dict()
            user_data["date"] = str(datetime.date.today())
            if client:
                myDatabaseDemo.create_document(user_data)
            return redirect('/')

    return render_template('error.html')


@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method == "POST":
        user = request.form['username']
        password = request.form['password']
        if user==admin_user and password==admin_password:
            try:
                all_data = Result(myDatabaseDemo.all_docs, include_docs=True)
            except:
                all_data = None
            return render_template('dashboard.html',all_data = all_data)
        else:
            return render_template('login.html') 
    return render_template('login.html')


# This method used to close the database connection when the application will be closed ...
@atexit.register
def shutdown():
    if client:
        client.disconnect()
        



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=port,debug=True)
    
