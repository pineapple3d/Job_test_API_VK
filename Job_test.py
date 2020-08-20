from flask import Flask, render_template,session, redirect, url_for, request
from markupsafe import escape
import json
import urllib3
import random


app = Flask(__name__)

#данные приложения

f = open ('keys.txt', 'r')
key = f.read()
app.secret_key = key[:key.find('\n')]
key = key[key.find('\n')+1:]
Vk_key = key[:key.find('\n')]
key = key[key.find('\n')+1:]
client_id = key[:key.find('\n')]

http = urllib3.PoolManager()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' in session:
        friends_request = http.request('GET','https://api.vk.com/method/friends.get?access_token='+str(session["user"]["access_token"])+'&v=5.122') 
        s = friends_request.data.decode('utf-8')
        friends_response = json.loads(s)
        ListOfFriends = friends_response["response"]["items"]
        request_string = 'user_ids='
        if friends_response["response"]["count"] < 6:
            for items in ListOfFriends:
                request_string += str (str(items)+',')
        else:
            LoF_short = []
            while len(LoF_short)<5:
                s = random.choice(ListOfFriends)
                try:
                    LoF_short.index(s)
                except:
                    LoF_short.append(s)
                    request_string += str (str(s)+',')
            request_string = request_string[:-1]
        friends_request_second = http.request('GET','https://api.vk.com/method/users.get?'+request_string+'&fields=first_name,last_name,photo_50&access_token='+str(session["user"]["access_token"])+'&v=5.122') 
        id_request = http.request('GET','https://api.vk.com/method/users.get?user_ids='+str(session['user']["username"])+'&fields=first_name,last_name,photo_50&access_token='+str(session["user"]["access_token"])+'&v=5.122') 
        temp1 = friends_request_second.data.decode('utf-8')
        friends_response_second = json.loads(temp1)
        temp2 = id_request.data.decode('utf-8')
        id_request = json.loads(temp2)
        list_to_show = friends_response_second["response"]
        myname = str(id_request["response"][0]['first_name']) + ' ' + str(id_request["response"][0]['last_name'])
        return (render_template('test.html', list_to_show=list_to_show, myname=myname))
    return '''
<form method="get">
<input type="image" name="image" src="https://sun9-70.userapi.com/2BXtn_391kIl0MQdBfsX3SWePCXIHh4cdHPb5Q/kPL8GE6wpmg.jpg" formaction="auth_VK" width="100">
        </form>
'''

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/auth_VK')
def auth_VK():
     return redirect('https://oauth.vk.com/authorize?client_id='+str(client_id)+'&display=page&redirect_uri=http://84.38.183.64:8081/callback&scope=friends&response_type=code&v=5.122')

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get("code")
    call_request = http.request('GET', 'https://oauth.vk.com/access_token?client_id='+str(client_id)+'&client_secret='+str(Vk_key)+'&redirect_uri=http://84.38.183.64:8081/callback&code='+str(code))
    s = call_request.data.decode('utf-8')
    callback_response = json.loads(s)
    session['user'] = {'username': callback_response['user_id'], 'access_token': callback_response['access_token']}
    return redirect('http://84.38.183.64:8081')

def StartServer():
 if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8081)

StartServer()
