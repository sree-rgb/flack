import os
import requests
from flask import Flask, jsonify, render_template, request, session, redirect,url_for
import datetime
from flask_socketio import SocketIO, emit,join_room,leave_room,disconnect
from flack_classes import *

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
socketio = SocketIO(app)

#users=[]
users=FlackUsers()
lastchannel={}
lastchannel2={}
chlist=[]
chmessages={}
diff='`~'
umessages={}
def privateId(uname1,uname2):
	"""
	Generates a unique chat id for chat involing two users.(Requires a seprator declared under diff variable)
	Takes two arguments which are usernames and sorts them and returns them with 'diff' used as separator
	""" 
	t_users=[uname1,uname2]
	t_users.sort()
	return diff+t_users[0]+diff+t_users[1]
def getUsers(id):return id.split(diff)[1:]

displaynamecheck=lambda :True if "user" in session else False
def dcheck(dname):
	"""
	checks for a valid display name.
	"""
	if dname:
		rules=[len(dname)> 2,dname[0].isalpha(),' ' not in dname,len(dname) < 20,\
		dname.isascii(),diff not in dname]
	else:
		rules=[False]
	return users.UserNotInUsers(dname) and all(rules)


@app.route("/")
def index():
	if not displaynamecheck():
		return redirect(url_for('displayname'))
	dname=session['user']

	return render_template("index.html",dname=dname)

@app.route("/displayname",methods=['GET'])
def displayname():
	if displaynamecheck():
		return redirect(url_for('index'))
	else:
		return render_template('displayname.html')

@app.route("/dnamecheck",methods=['POST'])
def dnamecheck():
	dname=str(request.form.get("dname"))
	return str(dcheck(dname))


@app.route("/getdname",methods=['POST'])
def getdname():
	if displaynamecheck():
		return 'redirect'
	dname=str(request.form.get("dname"))
	if dcheck(dname):
		session["user"]=dname


		# Fix here sends the same name which is not useful for
		with app.app_context():
			socketio.emit("new user",dname) #buggy needs to fixed uses js to stop sending sma username
		#users.append(dname)
		users.addUser(FlackUser(dname))
		return 'success'
	else:
		return 'fail'
@app.route("/clist",methods=['POST'])
def clist():
	#This verson has better way of forming response than 'css'.
	response={'status':'fail'}
	# if 'user' not in session:
	# 	response={'status':'fail'}
	if 'user' in session:
		user=session['user']
		response['status']='success'
		response['chlist']=chlist
		response['users']=users.stringList()

		# response={'status':'success','chlist':chlist,'users':users.getStringUserList()}

		if  user in lastchannel2:
			if lastchannel2[user][0:2] == diff:
				uname1,uname2=getUsers(lastchannel2[user])
				outUser=list(set([uname1,uname2])-set([session['user']]))[0]
				response['status']='private'
				response['otherUser']=outUser
				# response={'status':'private','chlist':chlist,'otherUser':outUser,'users':users.getStringUserList()}
			else:
				response['status']='reload'
				response['lastchannel']=lastchannel2[user]
				# response={'status':'reload','chlist':chlist,'lastchannel':lastchannel2[user],'users':users.getStringUserList()}
	return jsonify(response)




@app.route('/channel/<string:channelname>',methods=['POST'])
def channel(channelname):
	if displaynamecheck:
		lastchannel[session['user']]=channelname
		return jsonify(chmessages.get(channelname,False))
@app.route('/user/<string:uname>',methods=['POST'])
def userchat(uname):
	user=session['user']
	lastchannel[session['user']]=privateId(user,uname)
	if uname==user: #return false if both current username and user request for chat are same
		return False
	try:
		return_string=umessages[user].get(uname,False)
	except KeyError:
		return_string=False
	if return_string == False:
			(uname1,uname2)=getUsers(lastchannel[session['user']])
			umessages[uname1]=umessages.get(uname1,{})
			umessages[uname1][uname2]=umessages[uname1].get(uname2,[])
			umessages[uname2]=umessages.get(uname2,{})
			umessages[uname2][uname1]=umessages[uname1][uname2]
	return jsonify(umessages[user].get(uname,False))

@socketio.on('join')
def on_join():
	if displaynamecheck():
		username = session['user']
		if username in lastchannel2:
			print(username+' left '+lastchannel2[username])
			leave_room(lastchannel2[username])
		room=lastchannel[username]
		join_room(room)
		lastchannel2[username]=room
		print(username+' joined '+lastchannel[username])


@socketio.on("message send")
def sendmessage(data):
	if not displaynamecheck():
		return 'UserError'
	try:
		channelname=lastchannel2[session['user']]
		if channelname[0:2] == diff:
			uname1,uname2=getUsers(channelname)
			messages=umessages[uname1][uname2]
			messageTime=int(datetime.datetime.timestamp(datetime.datetime.now())*1000)
			message={"message":data,"sender":session["user"],"time":str(messageTime)}
			emit("recieve message",message,room=lastchannel2[session['user']])
			umessages[uname1][uname2].append(message)
			if len(umessages[uname1][uname2])>100:
				umessages[uname1][uname2].pop(0)
		else:
			messages=chmessages.get(channelname,[])
			chmessages[channelname]=messages # Intializing new channels
			messageTime=int(datetime.datetime.timestamp(datetime.datetime.now())*1000)
			message={"message":data,"sender":session["user"],"time":str(messageTime)}
			emit("recieve message",message,room=lastchannel2[session['user']])
			chmessages[channelname].append(message)
			if (len(chmessages[channelname])>100):
				chmessages[channelname].pop(0)
				print('message popped')
	except KeyError:
		return 'KeyError'

@socketio.on("channel add")
def channelAdd(channelname):
	#Was unable to add an action to indicate channel add fail, because of broadcast to every user.
	rules=[len(channelname.strip())>1]
	if not displaynamecheck():
		pass
	elif (channelname not in chlist) and all(rules) and (channelname.replace(' ','') not in chmessages) and channelname[0:2]!=diff:
		chlist.append(channelname)
		chmessages[channelname.replace(' ','')]=[]
		print('channel name added')
		emit("channel added",channelname,broadcast=True)
@socketio.on('connect')
def connect_handler():
	if not displaynamecheck():
		disconnect()

