class FlackUser:
	def __init__(self,displayname):
		self.displayname=displayname
	def __str__(self):
		return self.displayname
	def __eq__(self,other):
		return self.displayname == other.displayname 
	def matchname(self,name):
		return name==self.displayname
class FlackUsers:
	def __init__(self):
		self.users=[]
	def addUser(self,user):

		if user not in self.users:
			self.__dict__[str(user)]=user
			self.users.append(self.__dict__[str(user)])
		else:
			raise ValueError('User alread exists')
	def stringList(self):
		return list(map(str,self.users))
	def UserNotInUsers(self,uname):
		#match=list(filter(lambda x:x.matchname(uname),self.users))
		#return  len(match)==0
		return uname not in self.__dict__