from flask import Flask, flash, redirect, render_template, request, session, abort
import os, json
app = Flask(__name__)

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
      with open('data.json', 'w') as outfile:
          json.dump(dic,outfile)
      print jsonarray
      return render_template("result.html",result = result)

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'pass' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return student()

if __name__ == '__main__':
   app.secret_key = os.urandom(12)
   app.run(host='192.168.1.47', port = 80, debug = False)
