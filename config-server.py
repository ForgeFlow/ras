from flask import Flask, flash, redirect, render_template, request, session, abort
import os, json, socket
app = Flask(__name__)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def student():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('student2.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      dic = result.to_dict(flat=False)
      print dic
      print str(dic['user_name'][0])
      #file = open('test.txt','w')
      jsonarray = json.dumps(dic)
      with open('/home/pi/Raspberry_Code/data.json', 'w+') as outfile:
          json.dump(dic,outfile)
      print jsonarray
      return render_template("result2.html",result = result)

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form.get('Reset credentials') == 'Reset credentials':
        print "RESET PASS"
        return render_template('change.html')
    elif request.form.get('Log in') == 'Log in':
        print "LOGIN"
        json_file = open('/home/pi/Raspberry_Code/credentials.json')
        json_data = json.load(json_file)
        json_file.close()
        print json_data['new password'][0]
        if request.form['password'] == json_data['new password'][0] and request.form['username'] == json_data['username'][0]:
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return student()
    else:
        print "ELSE"
        return student()

@app.route('/change', methods=['POST', 'GET'])
def change_credentials():
    if request.method == 'POST':
      result = request.form
      dic = result.to_dict(flat=False)
      print dic
      #file = open('test.txt','w')
      jsonarray = json.dumps(dic)
      json_file = open('/home/pi/Raspberry_Code/credentials.json')
      json_data = json.load(json_file)
      json_file.close()
      print json_data['new password'][0]
      if str(dic['old password'][0]) == json_data['new password'][0] and str(dic['username'][0]) == json_data['username'][0]:
          with open('/home/pi/Raspberry_Code/credentials.json', 'w+') as outfile:
              json.dump(dic,outfile)
          print jsonarray
      else:
          flash('wrong password!')

      #print jsonarray['new password'][0]
      return student()


if __name__ == '__main__':
   app.secret_key = os.urandom(12)
   app.run(host=str(get_ip()), port = 80, debug = False)