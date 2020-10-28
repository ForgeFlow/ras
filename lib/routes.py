import json
import os
import subprocess
import logging
import time

from collections import OrderedDict

from flask import Flask, flash, render_template, request, session

from dicts.tz_dic import tz_dic

from werkzeug.serving import make_server

import threading
from . import Utils

_logger = logging.getLogger(__name__)

tz_sorted = OrderedDict(sorted(tz_dic.items()))

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        Utils.getOwnIpAddress()
        self.srv = make_server(str(Utils.settings["ownIpAddress"][0]), 3000, app)
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

	oldAdminCard = Utils.settings["odooParameters"]["admin_id"][0].lower()

	app = Flask("odoo_new_admin_card")
	app.secret_key = os.urandom(12)
	server = ServerThread(app)
	server.start()
	

	@app.route("/")
	def form():
		if session.get("logged_in"):
			return render_template("reset_admin_form.html", IP=str(Utils.settings["ownIpAddress"][0]), port=3000)
		else:
			return render_template("loginNewAdminCard.html", IP=str(Utils.settings["ownIpAddress"][0]), port=3000)

	@app.route("/loginNewAdminCard", methods=["POST", "GET"])
	def doLogin():
		if request.method == "POST":			
			if request.form.get("Log in") == "Log in":
				if (request.form["password"] == Utils.settings["flask"]["new password"][0]):
					session["logged_in"] = True
					return form()
				else:
					#flash("wrong password!")
					return form()
			else:
				return form()
		else:
			return form()

	@app.route("/adminCardChanged", methods=["POST", "GET"])
	def result():
		if request.method == "POST":
			if request.form.get("Log in") == "Log in":
				return form()
			else:
				results = request.form
				dic = results.to_dict(flat=False)
				newAdminCard = dic["admin_id"][0].lower()
				message = ["",""]

				if newAdminCard == oldAdminCard :
					#print("You just introduced the old Admin Card. Please introduce a new one.")
					message[0] = "You just introduced the old Admin Card."
					message[1] = "Please introduce a new Admin Card."
					defineAgain = True
					#print(message)
					return render_template("adminCardChanged.html", IP=str(Utils.settings["ownIpAddress"][0]), port=3000, adminCardChangeResult = message, defineAgain = defineAgain)
				else:
					Utils.settings["odooParameters"]["admin_id"] = dic["admin_id"]

					Utils.storeOptionInDeviceCustomization("odooParameters",Utils.settings["odooParameters"])

					#print("Succesfully updated the Admin Card.")
					message[0] = "The new Admin Card is " + dic["admin_id"][0]
					message[1] = "and was succesfully updated in Odoo."
					defineAgain = False

					exitFlag.set() # end all the threads
					return render_template("adminCardChanged.html", IP=str(Utils.settings["ownIpAddress"][0]), port=3000, adminCardChangeResult = message, defineAgain = defineAgain)
		else:
			return render_template("reset_admin_form.html", IP=str(Utils.settings["ownIpAddress"][0]), port=3000)

def startServerOdooParams(exitFlag):
	global server
	global app

	app = Flask("odoo_config_params")
	app.secret_key = os.urandom(12)
	server = ServerThread(app)
	server.start()
	
	@app.route("/")
	def form():
		if session.get("logged_in"):
			return render_template("form.html", IP=str(Utils.settings["ownIpAddress"][0]), port=3000, tz_dic=tz_sorted)
		else:
			return render_template("login.html")


	@app.route("/result", methods=["POST", "GET"])
	def result():
		if request.method == "POST":
			results = request.form
			dic = results.to_dict(flat=False)
			Utils.storeOptionInDeviceCustomization("odooParameters",dic)
			exitFlag.set() # end all the threads
			render_template("result.html", result=dic)
			time.sleep(2)
			server.shutdown()         
			return True
		else:
			return form()

	@app.route("/login", methods=["POST", "GET"])
	def do_admin_login():
		if request.method == "POST":			
			if request.form.get("Reset credentials") == "Reset credentials":
				return render_template("change.html")
			elif request.form.get("Log in") == "Log in":
				#print("routes 190 - do_admin_login, credentialsDic ", Utils.settings["flask"]["new password"][0], )
				if (request.form["password"] == Utils.settings["flask"]["new password"][0]):
					session["logged_in"] = True
				else:
					flash("wrong password!")
				return form()
			else:
				return form()
		else:
			return form()


	@app.route("/change", methods=["POST", "GET"])
	def change_credentials():
		if request.method == "POST":
			result = request.form
			dataFromTheForm = result.to_dict(flat=False)
			if (str(dataFromTheForm["old password"][0]) == Utils.settings["flask"]["new password"][0]):
					Utils.storeOptionInDeviceCustomization("flask", dataFromTheForm)
			else:
					flash("wrong password!")
			return form()
		else:
			return form()

def stop_server():
    global server
    server.shutdown()
