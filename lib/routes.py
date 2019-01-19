import json, os, subprocess

from collections import OrderedDict

from flask import Flask, flash, render_template, request, session

from dicts.tz_dic import tz_dic
from dicts.ras_dic import WORK_DIR

from lib import app

def get_ip():

    command = "hostname -I | awk '{ print $1}' "

    IP_address = subprocess.check_output(
            command, shell=True).decode('utf-8').strip('\n')

    return IP_address

@app.route('/')
def form():
    print('inside form')
    tz_sorted = OrderedDict(sorted(tz_dic.items()))
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if os.path.isfile(WORK_DIR+'dicts/data.json'):
            json_file = open(WORK_DIR+'dicts/data.json')
            json_data = json.load(json_file)
            json_file.close()
            return render_template('form.html', IP=str(get_ip()), port=3000,
                                   data=json_data, tz_dic=tz_sorted)
        else:
            return render_template('form.html', IP=str(get_ip()), port=3000,
                                   data=False, tz_dic=tz_sorted)


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        results = request.form
        dic = results.to_dict(flat=False)
        jsonarray = json.dumps(dic)
        with open( WORK_DIR+'dicts/data.json', 'w+') as outfile:
            json.dump(dic, outfile)
        return render_template("result.html", result=results)

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form.get('Reset credentials') == 'Reset credentials':
        return render_template('change.html')
    elif request.form.get('Log in') == 'Log in':
        json_file = open(WORK_DIR+'dicts/credentials.json')
        json_data = json.load(json_file)
        json_file.close()
        if request.form['password'] == json_data['new password'][0] and \
                request.form['username'] == json_data['username'][0]:
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return form()
    else:
        return form()

