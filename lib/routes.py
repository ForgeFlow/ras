import json
import os
import subprocess
import logging

from collections import OrderedDict

from flask import Flask, flash, render_template, request, session

from dicts.tz_dic import tz_dic

from werkzeug.serving import make_server

import threading
from . import Utils

_logger = logging.getLogger(__name__)


def get_ip():
    _logger.debug("Getting IP")
    command = "hostname -I | awk '{ print $1}' "

    ip_address = (
        subprocess.check_output(command, shell=True).decode("utf-8").strip("\n")
    )

    return ip_address

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server(str(get_ip()), 3000, app)
        self.ctx = app.app_context()
        self.ctx.push()
        _logger.debug("ServerThread Class Initialized")

    def run(self):
        _logger.debug("Serve forever")
        self.srv.serve_forever()

    def shutdown(self):
        _logger.debug("Shutdown")
        self.srv.shutdown()

def startServerAdminCard(exitFlag):
    global server
    global app
    global data

    data =Utils.getJsonData(Utils.WORK_DIR + "dicts/data.json")
    oldAdminCard = data["admin_id"][0].lower()

    app = Flask("odoo_config_params")
    app.secret_key = os.urandom(12)
    server = ServerThread(app)
    server.start()
    

    @app.route("/")
    def form():
        _logger.debug("inside form")
        tz_sorted = OrderedDict(sorted(tz_dic.items()))
        if not session.get("logged_in"):
            return render_template("loginNewAdminCard.html")
        else:
            return render_template(
                "form.html", IP=str(get_ip()), port=3000, tz_dic=tz_sorted
            )

    def reset_admin_form():
        _logger.debug("reset admin form")
        if not session.get("logged_in"):
            return render_template("loginNewAdminCard.html")
        else:
            return render_template("reset_admin_form.html", IP=str(get_ip()), port=3000)

    @app.route("/reset_admin_card", methods=["POST"])
    def reset_admin_card_result():
        if request.method == "POST":
            results = request.form
            dic = results.to_dict(flat=False)
            newAdminCard = dic["admin_id"][0].lower()

            if newAdminCard == oldAdminCard :
                flash("No valid AdminCard. Already in system")
                return reset_admin_form()

            data["admin_id"] = dic["admin_id"]

            Utils.storeJsonData(Utils.WORK_DIR + "dicts/data.json", data)

            exitFlag.set() # end all the threads

            return render_template("result.html", result=data)

    @app.route("/result", methods=["POST", "GET"])
    def result():
        if request.method == "POST":
            results = request.form
            dic = results.to_dict(flat=False)
            # with open(Utils.WORK_DIR + "dicts/data.json", "w+") as outfile:
            #     json.dump(dic, outfile)
            return render_template("result.html", result=dic)

    @app.route("/login", methods=["POST"])
    def do_admin_login():
        if request.form.get("Reset credentials") == "Reset credentials":
            return render_template("change.html")
        elif request.form.get("Log in") == "Log in":
            json_file = open(Utils.WORK_DIR + "dicts/credentials.json")
            json_data = json.load(json_file)
            json_file.close()
            if (
                request.form["password"] == json_data["new password"][0]
                and request.form["username"] == json_data["username"][0]
            ):
                session["logged_in"] = True
            else:
                flash("wrong password!")
            return form()
        elif request.form.get("Reset AdminCard") == "Reset AdminCard":
            json_file = open(Utils.WORK_DIR + "dicts/credentials.json")
            json_data = json.load(json_file)
            json_file.close()
            if (
                request.form["password"] == json_data["new password"][0]
                and request.form["username"] == json_data["username"][0]
            ):
                session["logged_in"] = True
            else:
                flash("wrong password!")
            return reset_admin_form()
        else:
            return form()

    @app.route("/change", methods=["POST", "GET"])
    def change_credentials():
        if request.method == "POST":
            result = request.form
            dic = result.to_dict(flat=False)
            print(dic)
            jsonarray = json.dumps(dic)
            json_file = open(Utils.WORK_DIR + "dicts/credentials.json")
            json_data = json.load(json_file)
            json_file.close()
            print(json_data["new password"][0])
            if (
                str(dic["old password"][0]) == json_data["new password"][0]
                and str(dic["username"][0]) == json_data["username"][0]
            ):
                with open(Utils.WORK_DIR + "dicts/credentials.json", "w+") as outfile:
                    json.dump(dic, outfile)
                print(jsonarray)
            else:
                flash("wrong password!")
            return form()

def startServerOdooParams(exitFlag):
    global server
    global app

    app = Flask("odoo_config_params")
    app.secret_key = os.urandom(12)
    server = ServerThread(app)
    server.start()
    

    @app.route("/")
    def form():
        _logger.debug("inside form")
        tz_sorted = OrderedDict(sorted(tz_dic.items()))
        if not session.get("logged_in"):
            return render_template("login.html")
        else:
            return render_template( "form.html", IP=str(get_ip()), port=3000, tz_dic=tz_sorted)

    @app.route("/result", methods=["POST", "GET"])
    def result():
        if request.method == "POST":
            results = request.form
            dic = results.to_dict(flat=False)
            Utils.storeJsonData(Utils.WORK_DIR + "dicts/data.json", dic)
            exitFlag.set() # end all the threads          
            return render_template("result.html", result=dic)

    @app.route("/login", methods=["POST"])
    def do_admin_login():
        if request.form.get("Reset credentials") == "Reset credentials":
            return render_template("change.html")
        elif request.form.get("Log in") == "Log in":
            data =Utils.getJsonData(Utils.WORK_DIR + "dicts/credentials.json")
            if (
                request.form["password"]     == data["new password"][0]
                and request.form["username"] == data["username"][0]
            ):
                session["logged_in"] = True
            else:
                flash("wrong password!")
            return form()
        else:
            return form()

    @app.route("/change", methods=["POST", "GET"])
    def change_credentials():
        if request.method == "POST":
            result = request.form
            dataFromTheForm = result.to_dict(flat=False)
            storedData = Utils.getJsonData(Utils.WORK_DIR + "dicts/credentials.json")
            if (    str(dataFromTheForm["old password"][0]) == storedData["new password"][0]
                    and str(dataFromTheForm["username"][0]) == storedData["username"][0]      ):
                Utils.storeJsonData(Utils.WORK_DIR + "dicts/credentials.json", dataFromTheForm)
            else:
                flash("wrong password!")
            return form()

def stop_server():
    global server
    server.shutdown()
