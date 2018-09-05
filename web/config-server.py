from flask import Flask, flash, redirect, render_template, request, session, abort, g
from flask_babel import Babel
import os, json, socket
app = Flask(__name__)

babel = Babel(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.

    json_file = open('/home/pi/ras/dicts/idiom.json')
    json_data = json.load(json_file)
    json_file.close()

    #return request.accept_languages.best_match(['es','en'])
    if json_data['language'][0] == "e":
        return json_data['language']
    else:
        return json_data['language'][0]

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
def form():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('form.html', IP=str(get_ip()), port=3000)

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      dic = result.to_dict(flat=False)
      print(dic)
      print(str(dic['user_name'][0]))
      jsonarray = json.dumps(dic)
      with open('/home/pi/ras/dicts/data.json', 'w+') as outfile:
          json.dump(dic,outfile)
      print(jsonarray)
      return render_template("result.html",result = result)

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form.get('Reset credentials') == 'Reset credentials':
        return render_template('change.html')
    elif request.form.get('Log in') == 'Log in':
        json_file = open('/home/pi/ras/dicts/credentials.json')
        json_data = json.load(json_file)
        json_file.close()
        print(json_data['new password'][0])
        if request.form['password'] == json_data['new password'][0] and request.form['username'] == json_data['username'][0]:
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return form()
    elif request.form.get('Change language') == 'Change language':
        result = request.form
        dic = result.to_dict(flat=False)
        json_file = open('/home/pi/ras/dicts/idiom.json')
        json_data = json.load(json_file)
        json_file.close()
        print(json_data['language'][0])
        with open('/home/pi/ras/dicts/idiom.json', 'w+') as outfile:
              json.dump(dic,outfile)
        return form()
    else:
        return form()

@app.route('/change', methods=['POST', 'GET'])
def change_credentials():
    if request.method == 'POST':
      result = request.form
      dic = result.to_dict(flat=False)
      print(dic)
      jsonarray = json.dumps(dic)
      json_file = open('/home/pi/ras/dicts/credentials.json')
      json_data = json.load(json_file)
      json_file.close()
      print(json_data['new password'][0])
      if str(dic['old password'][0]) == json_data['new password'][0] and str(dic['username'][0]) == json_data['username'][0]:
          with open('/home/pi/ras/dicts/credentials.json', 'w+') as outfile:
              json.dump(dic,outfile)
          print(jsonarray)
      else:
          flash('wrong password!')

      return form()


if __name__ == '__main__':
   app.secret_key = os.urandom(12)
   app.run(host=str(get_ip()), port = 3000, debug = False)
