# Makes use of bottle.py, available here: http://bottlepy.org/

from bottle import get, post, run, request, response, redirect, debug, \
  static_file
import xmlrpclib
from page import *

DB_ADDRESS = 'http://youface.cs.dixie.edu/'
DB_SERVER = xmlrpclib.ServerProxy(DB_ADDRESS, allow_none=True)

@get('/youface.css')
def stylesheet():
    return static_file('youface.css', root='./')

@post('/login')
def login():
    name = request.forms.get('name')
    password = request.forms.get('password')
    button = request.forms.get('type')
    response.set_cookie('name', name, path='/')
    response.set_cookie('password', password, path='/')
    if button == 'Create':
        (status, msg) = DB_SERVER.newUser(name, password)
    elif button == 'Delete':
        (status, msg) = DB_SERVER.deleteUser(name, password)
    redirect('/')

@post('/logout')
def logout():
    response.set_cookie('name', '', path='/')
    response.set_cookie('password', '', path='/')
    redirect('/')

@post('/status')
def status():
    name = request.COOKIES.get('name', '')
    password = request.COOKIES.get('password', '')
    status = request.forms.get('status')
    DB_SERVER.setStatus(name, password, status)
    redirect('/')

@post('/addfriend')
def addFriend():
    name = request.forms.get('name')
    userName = request.COOKIES.get('name', '')
    password = request.COOKIES.get('password', '')
    DB_SERVER.addFriend(userName, password, name)
    redirect('/')

@post('/unfriend')
def unFriend():
    name = request.forms.get('name')
    userName = request.COOKIES.get('name', '')
    password = request.COOKIES.get('password', '')
    DB_SERVER.unFriend(userName, password, name)
    redirect('/')

@get('/')
def getCookies():
    name = request.COOKIES.get('name', '')
    password = request.COOKIES.get('password', '')
    (status, friends) = DB_SERVER.listFriends(name, password)
    (status2, updates) = DB_SERVER.listStatusFriends(name, password, 25)
    if (status == 'failure' or status2 == 'failure'):
        redirect('/loginscreen')
    return str(FeedPage(name, updates, friends))

@get('/loginscreen')
def loginscreen():
    return str(LoginPage())

@get('/friend/:fname')
def friend(fname):
    name = request.COOKIES.get('name', '')
    password = request.COOKIES.get('password', '')
    (status, friends) = DB_SERVER.listFriends(name, password)
    (status2, updates) = DB_SERVER.listStatusUser(name, password, fname, 25)
    if (status == 'failure' or status2 == 'failure'):
        redirect('/loginscreen')
    return str(FriendPage(fname, updates, friends))

def main():
    global DB_SERVER, DB_ADDRESS

    print 'Using YouFace server at', DB_ADDRESS
    DB_SERVER = xmlrpclib.ServerProxy(DB_ADDRESS, allow_none=True)
    debug(True)
    run(host='localhost', port=8080, reloader=True)

if __name__ == '__main__':
    main()
