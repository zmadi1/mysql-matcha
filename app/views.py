from flask import jsonify,abort,make_response,render_template,url_for,flash,g, redirect,session,request,make_response
from app import app
# from flask_bcrypt import Bcrypt
from functools import wraps
import pyproj
import csv
from geopy import distance
from PIL import Image
from operator import itemgetter
import datetime

from flask_login import LoginManager
from app.forms import RegistrationForm,PostForm, LoginForm, UpdateAccountForm, UploadsForm, MessageForm,ForgotForm
from app.database import *
import secrets
import os
import json
import random
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO,send,emit,join_room, leave_room
import time
from time import localtime,strftime

from itsdangerous import SignatureExpired, URLSafeTimedSerializer
import re 
  
mail_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
# for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

username_regex = '\w' # fuck me sideways equivalent is '[a-zA-Z0-9_]'
firstname_regex = '[a-zA-Z]+'
passwd_regex = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$'
interest_regex = '^#'

# bcrypt = Bcrypt(app)
mail = Mail(app)



geod = pyproj.Geod(ellps='WGS84')

#Initialize the Flask-SocketIO
socketio = SocketIO(app)

ROOMS = ["lounge","news","games","coding"]



# @app.route('/identity')
# def identity():
#     id=session.get("USER") 
#     # existing_blog_post = find_blog_post(id_)
#     with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
#         cursor=cnx.cursor()
            
#         cursor.execute(find_user_by_id(id))
#         existing_user = cursor.fetchone()
#     return()

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'USER' in session:
            id = session.get("USER")
            s_id =secrets.token_urlsafe()
            with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                cursor = cnx.cursor()
                cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `status`(
                s_id VARCHAR(100) ,
                user_id VARCHAR(200) NOT NULL,
                status TEXT NOT NULL, 
                PRIMARY KEY(user_id),
                FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                )
                """
                )
                cnx.commit()
            with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                cursor = cnx.cursor()
                cursor.execute(f"INSERT IGNORE INTO `status`(`s_id`,`user_id`,`status`) VALUES('{s_id}','{id}',TRUE)")
                cnx.commit()
                
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_access(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not 'USER' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized', 'danger')
            return redirect(url_for('profile'))
    return wrap
# app.config['IMAGE_UPLOADS'] = '~/Documents/app/app/static/img'
# @app.route('/admin')
# def admin():

    #accessing the blogpost
    # users = User.objects(username='lunga').get()
    # posts = BlogPost.objects(author=users)


    # for post in posts:
    #     print(post.author.username,post.author.bio)
    # print('Done')

    #Query operators

    #less than & greater than

    # young_users = User.objects(age__lt=33)
    # for user in young_users:
    #     print(user.username,user.age)


    # older_users = User.objects(age__gte=30)
    # for user in older_users:
    #     print(user.username,user.age)

    #Query a list
    #we enter the name of the list that we're quering and then
    # we throw in the string that we're quering for if you 
    #are quering for a single value
    # post_tagged_python = BlogPost.objects(tags='MongoDB')

    # for post in post_tagged_python:
    #     print(post.title)

    #if you got multiple values that you want to query for
    # post_tagged_python = BlogPost.objects(tags__in=['MongoDB'])

    # for post in post_tagged_python:
    #     print(post.content)


    #String queries/case insensitive string(find a match)
    #we first provide the field we want to search,double underscore
    #because we're using query operator
    # python_posts = BlogPost.objects(content__icontains='python')

    # for post in python_posts:
    #     print(post.content)

    # python_posts = BlogPost.objects(title__icontains='my')

    # for post in python_posts:
    #     print(post.title)

    #contain is case sensitive
    # python_posts = BlogPost.objects(title__contains='first')

    # for post in python_posts:
    #     print(post.title)

    #Limiting and Skipping results
    # Get the first 

    #The first method is going to return the first document in the 
    #collection
    # first = BlogPost.objects.first()
    # print(first.title)

    #Get the first 2 documents/here we're going to use the python
    #slicing method

    # first_two = BlogPost.objects()[:2]

    # for post in first_two:
    #     print(post.title)

    #Get all but the first 2
    # all_but = BlogPost.objects()[2:]

    # for post in all_but:
    #     print(post.title)

    #sliced is very useful for pagination
    # sliced = BlogPost.objects()[2:4]

    # for post in sliced:
    #     print(post.title)

    #Counting

    # user_count = User.objects().count()
    # print(user_count)

    #Aggregation

    # average = BlogPost.objects.average('rating')
    # print(average)

    # total_rating = BlogPost.objects.sum('rating')
    # print(total_rating)

    # zakhele = User.objects(username='zakhele').get()
    # print(zakhele.json())




    # return render_template('admin/dash_board.html')


@socketio.on('join')
def join(data):

    print(data)
    # check = request.sid
    # print(check)
    # print(data)
    if data != {'user_name': {}, 'room': {}}:
        join_room(data['room'])
    print(data['room'])
    #When joining the room we receve this message automatically
    if data != {'user_name': {}, 'room': {}}:
        emit('my event',{'user_name':'chatbot','message':data['user_name'] + ' has joined the '+data['room'] + ' room.'},room=data['room'])

@socketio.on('leave')
def leave(data):

    if data != None:
        leave_room(data['room'])

    if data != None:
        emit('my event',{'user_name':'chatbot','message':data['user_name'] + ' has left the '+data['room'] + ' room.'},room=data['room'])

@socketio.on('open_profile')
def open_profile(data):

    liked_id = secrets.token_urlsafe()

    id = session.get('USER')

    #The person who their profile has been opened.
    post_id= data['user']


    print("????????????????????????????????????????????????????????")
    print(data)
    print(data['user'])
    # print(post_id)
    # current_user

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM  `users` WHERE `username`='{data['user']}'")

        user = cursor.fetchone()

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM  `users` WHERE `username`='{data['owner']}'")

        owner = cursor.fetchone()
    
    
 
    print(":::::::::::::::::::::::::::::this is where we are:::::::")
    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        # cursor.execute(f"INSERT INTO `liked`(`liked_id`,`user_id`,`username`,`epoch`) VALUES('{liked_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{other_user[0][1]}'), '{user[0][1]}','{data['time']}')")
        cursor.execute(f"INSERT INTO `liked`(`liked_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{liked_id}',(SELECT `user_id` FROM `users` WHERE `username`='{data['user']}'),'{data['owner']}','{data['id']}','{data['time']}')")
        cnx.commit()

    # print(f"{user}&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM `liked` WHERE `user_id` ='{user[0]}'")
        
        old_user=cursor.fetchall()
        cnx.commit()
        
    print(f"{old_user}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"{owner[0]}******************************************************************************************************")
    # print(other_username)
    # updating notification that someone has liked my profile
    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        # UPDATE users SET `age` = '{age}' WHERE `username`='{username}'
        cursor.execute(f"UPDATE  `users` SET `notification`='{old_user[0][0]}'  WHERE username='{data['user']}'")
        cnx.commit()
        
        
        # print(f"This is the room {other_user[0][1]}")

    print(data['user'])
    # push_user_open_your_profile(post_id,data)
    #push that someone has viewed my profile
    # push_user_liked_you(post_id,data)


    # current = find_user(post_id)
    #checking whether someone has viewd my profile
    # current = len(current['liked'])

    #updating notification that someone has liked my profile
    # notification_update(post_id,current)

    
    # print('hello')
    # print(user['username'])

    # noti_user = len(ola_user['liked'])
    # notification_update( ola_user['username'],ola_noti_user)

    # post = find_user(user_post)
    socketio.emit('notification',data,room=data['user'])
    # print("Phakathi inside we did it, what's is up bitches!!!!!!!!!")


    # print(data['user'])
    # socketio.emit('Profile',data,room=post_id)
    



@app.route('/message-send',methods=['GET','POST'])
def message():

    id = session.get('USER')

   




    form = MessageForm()

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()

        cursor.execute(f"SELECT `username` FROM `likes` WHERE `user_id`='{id}'")
        existing_user = cursor.fetchall()
    # print(existing_user)

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT `username` FROM `users` WHERE `user_id`='{id}'")
        
        user = cursor.fetchall()
    
    # print(f"{user[0][0]} hello--------------------------")

        # print(f"{user[0][0]} is the current user")
    
    # print(f"{existing_user[0][0]} this is what the current user is holding")


    
    rooms = []
    other_user = []
    print("hello world")
    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()    
        cursor.execute(f"SELECT `username` FROM `likes` WHERE `user_id`='{id}'")
        likes = cursor.fetchall()
        # other_user.append(k[0])

    print(f"{likes} these are the people i liked")



    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()    
        cursor.execute(f"SELECT `username` FROM `liked` WHERE `user_id`='{id}'")
        liked = cursor.fetchall()
        # other_user.append(k[0])

    print(f"{liked} these are the people who liked me")


    for i in likes:
        print(f"just checking likes ==={i[0]}")
        for k in liked:
            if i == k:
                rooms.append(i[0])
                print(f"just checking liked+++++++{k[0]}")
    
    rooms = list(dict.fromkeys(rooms))
    # if existing_user != []:
        # with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        #     cursor=cnx.cursor()
            
        #     cursor.execute(f"SELECT `user_id` FROM `users` WHERE `username`='{existing_user[0][0]}'")
        #     other_user = cursor.fetchall()

        # for i in existing_user:
        #     with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        #         cursor=cnx.cursor()    
        #         cursor.execute(f"SELECT `user_id` FROM `users` WHERE `username`='{i[0]}'")
        #         k = cursor.fetchone()

        #         other_user.append(k[0])

        #     # print(i[0])
        # print(f"{other_user} these are other users-----------------------------------------------------------------")

       

        # for i in other_user:
            # print(i)
        # print(f"{other_user}++++++++++++++++++ we're checking") 
        # if other_user !=[]:
            # with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            #     cursor=cnx.cursor()

            #     cursor.execute(f"SELECT `username` FROM `likes` WHERE `user_id`='{other_user[0][0]}'")
            #     other_user_likes = cursor.fetchall()

            # other_user_likes= []
            # for i in other_user:
            #     print(i)
            # print(f"{other_user}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            # for i in other_user:
                # print(i)
                # with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                    # cursor=cnx.cursor()    
                    # cursor.execute(f"SELECT `username` FROM `likes` WHERE `user_id`='{i}'")
                    # k = cursor.fetchall()
                # print(f"{k}++++++++++++++++++++++++++++++++=============================")
    
            # other_user_likes.append(k)
            # print(f"{other_user_likes} &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

            # with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            #     cursor=cnx.cursor()

            #     cursor.execute(f"SELECT `username` FROM `users` WHERE `user_id`='{other_user[0][0]}'")
            #     other_user_users = cursor.fetchall()
            # other_user_users=[]
            # for i in other_user:
            #     print(i)
            #     with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            #         cursor=cnx.cursor()    
            #         cursor.execute(f"SELECT `username` FROM `users` WHERE `user_id`='{i}'")
            #         k = cursor.fetchone()

            #         other_user_users.append(k[0])

            # print(f"{other_user_users}************************************************************")
    
    # print(f"'{other_user_likes[0][0]}' this is what the other person is holding")
    # print(other_user_users[0][0])
   
            # print(other_user_likes)
            # print(f"This is the current user {user}")
            # print(existing_user)
            # print(other_user_likes)
            # print(user)
            # print(other_user_likes )

            # for k in existing_user:
            #     # print(k[0])

            #     for i in other_user_likes:
            #         for j in i:

            #             # print(j[0])
            #             if user[0][0] == j[0]:
            #                 rooms.append(k[0])
                        # print("We did make it here")
                 
                        # print(i[0])
            # if user and other_user_likes ('mapula',), ('Tshepo',)]!=[]:
                # print(other_user)
                # for i in other_user_likes:
                #     # print(f"{i[0]} this are the users")
                #     if user[0][0]==i:
                #         if existing_user and other_user_users !=[]:
                #             if existing_user[0][0] == other_user_users[0][0]:
                #                 rooms.append(other_user_users[0][0])
                #                 print("You have both liked each other")
        

    # print(rooms)

    # print("||||||||||||||||||||||||||")
    # print(other_user_users[0][0])
    # print("|||||||||||||||||||||||||||")
    # print()

        # print("they can chat")
    
    # print("-----------------")
    # print(existing_user[0][0])
    # print(other_user_likes[0][0])
    # print("-----------------")
    # print(other_user_likes[0][2])
    # print(other_user_likes[0][2])

    # existing_blog_post = find_blog_post(i
    # user = existing_user['username']

    

    # for i in existing_user['liked']:
    #     if i['id'] == 'like':
    #         other_user = find_user(i['owner'])
    #         for k in other_user['liked']:
    #             if k['id'] == 'like':
    #                 if existing_user[0][2] == i['user']:
    #                     # print(k['owner'])
    #                     # print('--------------------------------')
    #                     # print(i['user'])
    #                     rooms.append(i['owner'])

    # rooms = list(dict.fromkeys(rooms))
    
    # msg = collection()


    return render_template('public/chat.html',rooms=rooms,user=user[0][0])

def collection():
    user = session.get('USER')

    active_user = find_id_for_session(user)
    
    # chat = []
    # for i in user:
    #     chat.append(i['messages'])

    # all_chat = []
    # for l in  active_user:
    #     for k in l:
    #         all_chat.append(k)
    #         print(k)
    all_chat = active_user['messages']
    return sorted(all_chat,key=itemgetter('time'))



@socketio.on('my event')
def handle_event(data):
    id = session.get("USER")

    message_id =secrets.token_urlsafe()
    if data is not None:
        messages = data
        print(data['room'])
        print(messages)
        if messages != {}:

            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()


                #   CREATE TABLE IF NOT EXISTS `pictures`(
                # pictures_id VARCHAR(100) ,
                # user_id VARCHAR(200) NOT NULL,
                # picture VARCHAR(100), 
                # PRIMARY KEY(pictures_id),
                # FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                # )


                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `messages`
                (
                    message_id VARCHAR(200) NOT NULL,
                    user_id VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    epoch VARCHAR(250) NOT NULL,  
                    PRIMARY KEY(message_id),
                    FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                )""")
                cnx.commit()
            
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
                cursor.execute(f"""
                INSERT INTO  `messages`(`message_id`,`user_id`,`message`,`username`,`epoch`)
                VALUES('{message_id}','{id}','{messages['message']}','{messages['room']}','{messages['time']}')
                """)
                cnx.commit()


            # push_user_messages(id,messages)
            # push_owner_messages(data['room'],messages)
            emit('my event',{'user_name':data['user_name'],'message':data['message'],'time_stamp':strftime('%b-%d %I:%M%p',localtime())},room=data['room'],broadcast=False)
    # print(data)


@socketio.on('like')
def handle_my_custom_event(data):
    likes_id = secrets.token_urlsafe()
    liked_id = secrets.token_urlsafe()
    # getting the usernames
    username = data['owner']
    other_username = data['user']

    # print(f"This belong to {other_username}")

    # getting the current user
    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor() 
        cursor.execute(f"SELECT * FROM `users` WHERE `username`='{username}'")
        
        user = cursor.fetchall()


    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor() 
        cursor.execute(f"SELECT * FROM `users` WHERE `username`='{other_username}'")
        
        other_user = cursor.fetchall()

    
    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor() 
        cursor.execute(f"SELECT * FROM `liked` WHERE `username`='{user[0][1]}'")
        
        you_liked = cursor.fetchall()

    # print(you_liked)
    print(other_user)
    # print(user[0][0])
    if you_liked !=[]:
        for i in you_liked:
            if i[1] != other_user[0][0]:
                if i[3] != data['id']:

            
                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor=cnx.cursor()
                        cursor.execute(f"INSERT INTO `likes`(`likes_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{likes_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{user[0][1]}'), '{other_user[0][1]}','{data['id']}','{data['time']}')")

                        cnx.commit()




                    #Recording that i have liked someone
                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor=cnx.cursor()
                        cursor.execute(f"INSERT INTO `liked`(`liked_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{liked_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{other_user[0][1]}'), '{user[0][1]}','{data['id']}','{data['time']}')")

                        cnx.commit()
                
                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor=cnx.cursor()
                        cursor.execute(f"SELECT COUNT(*) FROM `liked` WHERE user_id ='{other_user[0][0]}'")

                        old_user=cursor.fetchall()
                        cnx.commit()
        
                    print(old_user[0][0])
                    print(other_username)
                    # updating notification that someone has liked my profile
                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor=cnx.cursor()
                        # UPDATE users SET `age` = '{age}' WHERE `username`='{username}'
                        cursor.execute(f"UPDATE  `users` SET `notification`='{old_user[0][0]}'  WHERE username='{data['user']}'")
                        cnx.commit()


                    # print(f"This is where the ids are not the same")
                    # print("What just happend????????????????????????????")
                    socketio.emit('notification',data,room=other_user[0][1])
        else:
            if i[3] != data['id']:
                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                    cursor=cnx.cursor()
                    cursor.execute(f"INSERT INTO `likes`(`likes_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{likes_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{user[0][1]}'), '{other_user[0][1]}','{data['id']}','{data['time']}')")

                    cnx.commit()




                #Recording that i have liked someone
                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                    cursor=cnx.cursor()
                    cursor.execute(f"INSERT INTO `liked`(`liked_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{liked_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{other_user[0][1]}'), '{user[0][1]}','{data['id']}','{data['time']}')")

                    cnx.commit()
                
                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                    cursor=cnx.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM `liked` WHERE user_id ='{other_user[0][0]}'")
        
                    old_user=cursor.fetchall()
                    cnx.commit()
        
                print(old_user[0][0])
                print(other_username)
                # updating notification that someone has liked my profile
                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                    cursor=cnx.cursor()
                    # UPDATE users SET `age` = '{age}' WHERE `username`='{username}'
                    cursor.execute(f"UPDATE  `users` SET `notification`='{old_user[0][0]}'  WHERE username='{data['user']}'")
                    cnx.commit()


                # print(f"This is where the ids are not the same.")
                
                socketio.emit('notification',data,room=other_user[0][1])
            else:
                print("This is where we are")
                print("The id's are the same.")
             
    else:
        # print("What just happend????????????????????????????")
        with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
            cursor=cnx.cursor()
            cursor.execute(f"INSERT INTO `likes`(`likes_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{likes_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{user[0][1]}'), '{other_user[0][1]}','{data['id']}','{data['time']}')")
            cnx.commit()


        #Recording that i have liked someone
        with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
            cursor=cnx.cursor()
            cursor.execute(f"INSERT INTO `liked`(`liked_id`,`user_id`,`username`,`status`,`epoch`) VALUES('{liked_id}' , (SELECT `user_id` FROM `users` WHERE `username`='{other_user[0][1]}'), '{user[0][1]}','{data['id']}','{data['time']}')")
            cnx.commit()
                
        with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
            cursor=cnx.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `liked` WHERE user_id ='{other_user[0][0]}'")

            old_user=cursor.fetchall()
            cnx.commit()
        
        print(old_user[0][0])
        print(other_username)
        # updating notification that someone has liked my profile
        with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
            cursor=cnx.cursor()
            # UPDATE users SET `age` = '{age}' WHERE `username`='{username}'
            cursor.execute(f"UPDATE  `users` SET `notification`='{old_user[0][0]}'  WHERE username='{data['user']}'")
            cnx.commit()
                    
                    
        print(f"This is the room {other_user[0][1]}")
        socketio.emit('notification',data,room=other_user[0][1])



    
   




@app.template_filter('low')  
def low(t):
    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(t)/1000.0))

@app.route('/jinja')
def jinja():

    

    id = session.get('USER')

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        
        cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
        existing_user = cursor.fetchone()
    


    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM `liked` WHERE user_id ='{id}'")
        
        old_user=cursor.fetchall()
        cnx.commit()
    

    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM `users` WHERE user_id ='{id}'")
        
        user=cursor.fetchall()
        cnx.commit()
        
    print(old_user[0][0])
    # print(other_username)
    # updating notification that someone has liked my profile
    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        # UPDATE users SET `age` = '{age}' WHERE `username`='{username}'
        cursor.execute(f"UPDATE  `users` SET `notification_numb`='{old_user[0][0]}'  WHERE username='{user[0][1]}'")
        cnx.commit()

    
    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        # UPDATE users SET `age` = '{age}' WHERE `username`='{username}'
        cursor.execute(f"SELECT * FROM  `users`  WHERE user_id='{id}'")
        notification_numb=cursor.fetchall()

        # cnx.commit()
    

    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM `liked` WHERE user_id ='{id}'")
        
        Profile=cursor.fetchall()
    
    Profile = sorted(Profile,key=itemgetter(4))
    Profile.reverse()
    # for i in profile:
    #     print(i)
    

    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # for i in Profile:
    #     print(i)

    # existing_user =  find_id(id)


    # profile = []
    # for i in existing_user['liked']:
        # user = find_user(i['owner'])
        # profile.append(i)
    
        # for k in existing_user['profile_open']:
        #     # user = find_user(k['owner'])
        #     profile.append(k)
        #     break
          

    # if len(existing_user['liked']) == 0:
    # for k in existing_user['profile_open']:
    #     profile.append(k)
       

    # notification_numb = existing_user['notification']

    # insert_notification(id,notification_numb)

    my_name = 'madi'

    age = 38

   
    

    langs = ["python","Javascript","Bash","c","Ruby"]
      
    friends = {
        "Tom":30,
        "Ally":60,
        "Tony":56,
        "Chelsea":28
    }
    colours = ('red','green')

   

    cool = True
    class gitremote:
        

        def __init__(self, name, discription, url):
            self.name = name
            self.discription =discription
            self.url = url
        def pull(self):
            return f'pullin repo {self.name}'
        def clone(self):
                return f'cloning into {self.url}'
        

    my_remote = gitremote(
        name='flask',
        discription='template design tutorial',
        url='https://github.com/jinja'
    )
    def repeat(x,qty):
        return x *  qty

    date = datetime.utcnow()

    my_html ='<h1>This is some HTML</h1>'

    suspicious = '<script>alert("YOU GOT HACKED")</script>'

    return render_template('public/jinja.html',notification_numb=existing_user[-1],Profile=Profile,suspicious=suspicious,my_html=my_html,date=date,age= age,cool=cool,my_remote=my_remote ,my_name= my_name,
    langs=langs,friends=friends,colours=colours,gitremote=gitremote,repeat=repeat
    )

@app.route('/sign-up',methods=['GET','POST'])
def sign_up():


    if request.method == 'POST':
        req = request.form

        username = req['username']
        email = req.get('email')
        password = request.form['password']

        return redirect(request.url)
    return  render_template('public/sign_up.html')

users = {
    "mitsuhiko": {
        "name": "Armin Ronacher",
        "bio": "Creatof of the Flask framework",
        "twitter_handle": "@mitsuhiko"
    },
    "gvanrossum": {
        "name": "Guido Van Rossum",
        "bio": "Creator of the Python programming language",
        "twitter_handle": "@gvanrossum"
    },
    "elonmusk": {
        "name": "Elon Musk",
        "bio": "technology entrepreneur, investor, and engineer",
        "twitter_handle": "@elonmusk"
    }
}


# @app.route('/profile/<username>')
# def profile(username):

#     user = None

#     if username in users:
#         user = users[username]

#     return render_template('public/profile.html',username=username,user=user)

@app.route('/multiple/<foo>/<bar>/<baz>')
def multi(foo, bar, baz):
    return f'foo is {foo}, bar is {bar}, baz is {baz}'

@app.route('/json',methods=['POST'])
def json():
    if request.is_json:

        req = request.get_json()
        response = {
            "message":"JSON recieved",
            "name":req.get('name')
        }

        #josonify takes any python strings,list, dictionary and convert to JSON
        res = make_response(jsonify(response),200)

        return res
    else:
        res = make_response(jsonify("{'message':'No JSON received'}"),400)
        return "No JSON received",400

@app.route('/landing',methods=['GET','POST'])
def landing():
    if session.get('USER',None) is not None:
      
        return render_template('public/landing_page.html')
    else:
        print("Userename not found in session")

@app.route('/landing/create-entry',methods=['POST'])
def create_entry():
    
    req = request.get_json()

    print(req)
    user = User.objects(id=session["USER"])
    print(user)
    # if req['bio'] and req['age'] != " ":
    #     user.update_one(set__bio=req['bio'])
    #     user.update_one(set__age=req['age'])
    #     flash('Information updated','success')
    #     #return redirect(url_for('profile'))
    # else:
    #     flash("Sorry you have to update the missing information before moving foward","danger")
  
    # res = make_response(jsonify(req),200)


    return render_template(url_for('profile'))

# https://duckduckgo.com/?t=ffab&q=querystring&ia=web

@app.route('/query')
def query():

    print(request.query_string)

    return render_template("public/create_post.html")

    # if request.args:
    #     args = request.args

    #     serialized = ", ".join(f'{k}: {k}'for k, v in args.items())
    #     return f'(Query) {serialized}',200
    # else:
    #     return "No query received",200

        # if 'title' in args:
        #     #title = request.args.get('title')
        #     title = args['title']
        # print(title)
    # for k, v in args.items():
    #     print(F"{k}:{v}")

    # if "foo" in args:
    #     foo = args.get('foo')

    # print(foo)



# Validators
def check_mail(email):  
    if(re.search(mail_regex,email)):  
        return True           
    else:  
        return False

def check_username(username):  
    if(re.search(username_regex,username)):
        if len(username) > 1:
            if len(username) < 31:   
                return True  
    else:  
        return False

def check_first_last_name(firstname):  
    if(re.search(firstname_regex,firstname)):
        if len(firstname) > 1:
            if len(firstname) < 31:   
                return True  
    else:  
        return False

def check_passwd(passwd): 
    pat = re.compile(passwd_regex)       
    mat = re.search(pat, passwd)  
    if mat: 
        return True 
    else: 
        return False 

def check_interest(interest):  
    if(re.search(interest_regex,interest)):  
        return True           
    else:  
        return False

def check_bio(bio):  
    if(re.search(firstname_regex,bio)):
        if len(bio) > 3:
            if len(bio) < 401:   
                return True  
    else:  
        return False

def check_gender(gender):  
        if gender == 'Male':
            return True
        elif gender == 'Female':   
            return  True
        elif gender == 'Other':  
            return True
        else:  
            return False

def check_sexualP(sexualPreference):
        if sexualPreference == 'Male':
            return True
        elif sexualPreference == 'Female':   
            return True
        elif sexualPreference == 'Bisexual':  
            return True
        elif sexualPreference == None:
            return True
        else:  
            return False

def check_where():

    id = session["USER"] 

    try:
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()

            cursor.execute(find_user_by_id(id))
            username = cursor.fetchone()

            cursor.execute(find_registered(username[0]))
            registered = cursor.fetchone()
            print(username)
            if registered[0] == 1:
                return  True
            else:
                return False
            
        cursor.close()
    except mysql.connector.Error as err:
        print(err)

@app.route('/registration',methods=['POST','GET'])
@is_access
def registration():
    form=RegistrationForm()

    if request.method =='POST':
        email = form.email.data
        username = form.username.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if check_username(username):
            if check_first_last_name(firstname):
                if check_first_last_name(lastname):
                    if check_mail(email):
                        if check_passwd(password):
                            if confirm_password == password:
                                if create_users(form):
                                    token = session.get("TOKEN")
                                    msg = Message('Confirm Email',sender='Matcha dating services', recipients=[email])
        
                                    link  = url_for('confirm_email',token=token, _external=True)
        
                                    msg.body=f"Your link is '<a><p><a href='{link}'>'{ link }'</a></p></a>'"

                                    mail.send(msg)

                                    return redirect(url_for('login'))
                            else:
                                flash('The two passwords provided do not match, please try again.', 'danger')
                        else:
                            flash('The password field should have at least one number', 'danger')
                            flash('At least one uppercase and one lowercase character', 'danger')
                            flash('At least one special symbol and be between 6 to 20 characters long', 'danger')
                            flash('Be between 6 to 20 characters long, please try again', 'danger')
                    else:
                        flash('The email address is invalid, please try again','danger')
                else:
                    flash('The lastname field must be between 2 to 30 characters long and can only contain English alphabet characters, please try again', 'danger')
            else:
                flash('The firstname field must be between 2 to 30 characters long and can only contain English alphabet characters, please try again', 'danger')    
        else:
            flash('The username field must be between 2 to 30 characters long and can be AlphaNumeric, please try again', 'danger')                     
    return render_template('public/registration.html',form=form,title='SignUp')


#email verification
@app.route('/confirm_email/<token>')
def confirm_email(token):

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        
        cursor.execute(f"SELECT COUNT(user_id) FROM `users` WHERE `tokenCode`= '{token}'")
        check_token = cursor.fetchone()

        print("Helllakdjfaldklfakdla_________________________________________________")
        print(check_token[0])

        try:
            if check_token[0] > 0:
                cursor.execute(f"UPDATE `users` SET  `AccountVerification` = 1 WHERE `tokenCode` = '{token}'")
                cnx.commit()
                # Close connection
                # token = s.dumps(email,salt='email-confirm')
                # email = s.loads(token,salt='email-confirm', max_age=600)
                return redirect(url_for('login'))
        except SignatureExpired:
            return 'nothing was the same'
    return "success"

@app.route('/confirmer/<token>/<changed>/<email>')
def confirmer(token,changed,email):

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        
        cursor.execute(f"SELECT COUNT(user_id) FROM `users` WHERE `tokenCode`= '{token}'")
        check_token = cursor.fetchone()
        # try:
        if check_token[0] > 0:
            changed = bcrypt.generate_password_hash(changed).decode('utf-8')
            cursor.execute(f"UPDATE `users` SET  `AccountVerification` = 0 WHERE `tokenCode` = '{token}'")
            cursor.execute(f"UPDATE `users` SET `password` = '{changed}' WHERE `tokenCode` = '{token}'")
            cnx.commit()

            msg = Message('Confirm Email',sender='Matcha dating services', recipients=[email])
        
            link  = url_for('confirm_email',token=token, _external=True)
        
            msg.body=f"Your link is '<a><p><a href='{link}'>'{ link }'</a></p></a>'"

            mail.send(msg)
            return redirect(url_for('login'))
        # except:
            # return 'nothing was the same'
    return "success"

@app.route('/forgotpass',methods=['POST','GET'])
@is_access
def forgot_pass():

    form = ForgotForm()
    
    email = form.email.data
    password = form.password.data
    confirm_password = form.confirm_password.data
    
    try:
        if request.method =='POST':

            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()

                cursor.execute(count_email(email))
                email_number = cursor.fetchone()
                
                cursor.execute(f"SELECT `tokenCode` FROM `users` WHERE `email`= '{email}'")
                token = cursor.fetchone()
            
            if email_number[0] == 1:
                if check_passwd(password):
                    if confirm_password == password:
                        if token[0]:
                            link  = url_for('confirmer',token=token[0],changed=password,email=email, _external=True)
                            msg = Message('Change password',sender='Matcha dating services', recipients=[email])
                            msg.body=f"Hi there, you have received this email because a request to change your password was made.<br> Click here <a href='{link}' target='_blank'>Change Password</a> to confirm your new set password, If you did NOT make that requst<br> kindly IGNORE this email."
                            mail.send(msg)
                            flash('Password changed successfull, to apply the changes please click on the email link that we have sent you.', 'success')
                            return redirect(url_for('login'))
                        else:
                            flash('Something does not add up regarding your account', 'danger')
                            return redirect(url_for('forgotpass'))
                    else:
                        flash('Your passwords do not match, please try again.', 'danger')
                        return redirect(url_for('forgotpass'))
                else:
                    flash('The password provided does not meet minimum password complexity requirements, please try again.', 'danger')
                    return redirect(url_for('forgotpass'))
            else:
                flash('Password changed successfull, to apply the changes please click on the email link that we have sent you.' 'success')
                return redirect(url_for('forgotpass'))
        else:
            return render_template('public/forgotpass.html',form=form)
    except:
        flash('Sorry smething went wrong.', 'danger')
        return render_template('public/forgotpass.html',form=form)

@app.route('/',methods=['POST','GET'])
@is_access
def login():
    
    form=LoginForm()

    if request.method== 'POST':
        try:
            if user_login(form) == True:
                flash('You have logged in ','success')
                return redirect(url_for('profile'))
            else:
                return redirect(request.url)
        except TypeError:
            flash("The Username or Password field is incorrect",'danger')
            return redirect(request.url)         
    else:
        return render_template('public/login.html',form=form)

def allowed_image(filename):
    
    #I want to make sure that ther's a "."
    #in the filename
    if not "." in filename:
        return False
    #else i want to split the extension from
    #the filename//split from the right and
    #from the (".",1)the right and take the
    #first element 
    ext = filename.rsplit(".",1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


@app.route('/upload-image',methods=['GET','POST'])
@is_logged_in
def upload_image():

    
    if request.method == 'POST':
        if request.files:

            if not allowed_image_filesize(request.cookies.get('filesize')):
                flash('File exceeded maximum size','danger')
                return redirect(request.url)

            image = request.files['image']

            if image.filename == "":
                flash("Image must have a filename",'danger')
                return redirect(request.url)
            #The .save is just a method on the file storage object that can
            #be seen by print(image)
            #The we give the method where we want to save our image
            #.filename is an attributte of the filestorage object which is holding 
            #into our image
            if not allowed_image(image.filename):
                flash("That image extension is not allowed",'danger')
                return redirect(url_for('profile'))
            else:
                #This here will senetize the filename
                #avoid nasty uploads
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['IMAGE_UPLOADS'],filename))
                
                #With this alone we don't have control of what kind of images are being uploaded
                #print('Image saved')
                id = session.get('USER')
                # print(id)
                find = existing_user(id)
                user = find['username']
                # print(user)
                # user = User.objects(id=session["USER"])
                # update_one({'id':user},{'$set':{'profile':filename}})
                upload_profile_pic(user,filename)

                # user.update_one(set__profile_pic=filename)

            return redirect(url_for('profile'))


    return render_template('public/upload_image.html')



# @app.route('/cookies')
# def cookies():

#     cookies = request.cookies

#     #This will throw an error when the cookie doesn't exist or if it
#     #has expired
#     # flavor = cookies['flavor']

#     life = cookies.get('life')
#     print(life)

#     #anything you would pass a return statement inside a python file
#     #you can pass it into make_response
#     res = make_response('Cookies',200)

#     res.set_cookie(
#         'flavor',
#         value='chocolate chip',
#         max_age =10,
#         expires=None,
#         path=request.path,
#         domain=None,
#         secure=False,
#         httponly=False,
#         samesite=False
#         )

#     res.set_cookie("chocoloate type","dark")
#     res.set_cookie("cheary","yes")

#     return res


@app.route('/profile',methods=['GET','POST'])
@is_logged_in
def profile():

    try:
        if check_where() == True:
            if session.get('USER',None) is not None:

                id=session.get("USER")

                with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                    cursor=cnx.cursor()
            
                    cursor.execute(find_user_by_id(id))
                    username = cursor.fetchone()
            
                    cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{id}'")
                    profile_pic = cursor.fetchall()
            
                    cnx.close()




                print(profile_pic)        
                with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                    cursor=cnx.cursor()    
                    cursor.execute("SELECT * FROM users")
                    all_user = cursor.fetchall()
            
                if profile_pic ==[]:
                    profile = "user.png"
                else:
                    profile = profile_pic[0][0]
        
        
                users = []
                posts = []
                interest = []
                inter = []
                interest_return =[]

                for pic in all_user:

                    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                        cursor=cnx.cursor()
                
                        cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
                        existing_user = cursor.fetchone()

                    if pic[13] is not None:
                        users_i = pic[13].split(',')
    
                    user_k = existing_user[13].split(',')
          
                    if pic[13] is not None:
                        for k in users_i:
                            interest_return.append(k)
            
           
                    if pic[1] != existing_user[1]:
          
                        if existing_user[11] == pic[10]:
                            for i in users_i:#other user interest
                                for k in user_k:#current user interest
                                    if i == k:
                                        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                                            cursor=cnx.cursor()
                                    
                                            cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{pic[0]}'")#other user pic
                                    
                                            picture = cursor.fetchall()
                                    
                                        if pic[1] in users:
                                            continue
                                        else:
                                            if picture != []:
                                                users.append(pic[1])#
                                                posts.append(picture[0])#
            
                gis_id =secrets.token_urlsafe()

                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                    cursor = cnx.cursor()
                    cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS `distance`(
                    d_id VARCHAR(100) ,
                    user_id VARCHAR(200) NOT NULL,
                    distance FLOAT NOT NULL, 
                    PRIMARY KEY(user_id),
                    FOREIGN KEY(d_id) REFERENCES `users`(user_id)
                    )
                    """
                    )
                    cnx.commit()
        
                if request.is_json:
                    req = request.get_json()
                    print(f"{req} this is the location zakhele you are the best")

                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor=cnx.cursor()
                        cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS `location`(
                        gis_id VARCHAR(100) ,
                        user_id VARCHAR(200) NOT NULL,
                        lat FLOAT NOT NULL,
                        lon FLOAT NOT NULL,
                        city TEXT NOT NULL,
                        PRIMARY KEY(gis_id),
                        FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                        )
                        """
                        )
                        cnx.commit()

                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor = cnx.cursor()
                        cursor.execute(f"SELECT COUNT(*) FROM `location` WHERE `user_id`='{existing_user[0]}'")
                        length = cursor.fetchall()
            
                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor = cnx.cursor()
                        cursor.execute(f"SELECT COUNT(*) FROM `location`")
                        old_length = cursor.fetchall()

                    if length[0][0] == 0:
                        with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                            cursor = cnx.cursor()

                            cursor.execute(f"""INSERT INTO `location`(`gis_id`,`user_id`,`lat`,`lon`,`city`)  VALUES("{gis_id}","{existing_user[0]}","{req['lat']}","{req['long']}","{req['ct']}")""")
                            cnx.commit()

                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor = cnx.cursor()
                        cursor.execute(f"SELECT `lat`, `lon` FROM `location` WHERE `user_id`= '{id}'")
                
                        location = cursor.fetchone()
        
                    data = {'lat':location[0],'lon':location[1]}


                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor = cnx.cursor()
                        cursor.execute(f"SELECT  `lat`, `lon` ,`user_id` FROM `location`")
                
                        users = cursor.fetchall()
            

                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor = cnx.cursor()
                        cursor.execute(f"SELECT  COUNT(*) FROM `location`")
                
                        location_length = cursor.fetchall()

                    d = []
                    coord =[]
                    data1=[]
                    c=[]


                    if old_length[0][0] == location_length[0][0]:
                        okc_ok = (data['lat'],data['lon'])
                        for post in users:
                            if post[2] != id:

                                coord.append(post[2])

                                norman_ok = (post[0], post[1])


                                d.append(distance.distance(okc_ok , norman_ok ).km)

                                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                                    cursor = cnx.cursor()
                                    cursor.execute(f"INSERT IGNORE INTO `distance`(`d_id`,`user_id`,`distance`)  VALUES('{id}',(SELECT `username` FROM `users` WHERE `user_id`='{post[2]}'),'{distance.distance(okc_ok , norman_ok ).km}')")
                                    cnx.commit()

                    response = make_response(jsonify(data))
                    return response
                with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                    cursor = cnx.cursor()
                    cursor.execute(f"SELECT  * FROM `distance`")
    
                    database1 = cursor.fetchall()
                for i in database1:
                    print(i)

            return render_template('public/profile.html',database1=database1,interest_return= interest_return,notification=existing_user[-2],notification_numb=existing_user[-1],existing_user=existing_user,posts=posts,profile=profile, users=users, user=session["USER"],username=username, isIndex=True)
        else:
            flash("You need to fill in all your information on this page before you are granted access to any page within the app.",'danger')
            return redirect(url_for('update')) 
    except:
        flash("Something went wrong.",'danger')
        return redirect(url_for('profile'))

@app.route('/gen_male',methods=['GET','POST'])
@is_logged_in
def gen_male():

    if session.get('USER',None) is not None:

        id=session.get("USER")

        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
                
            cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
            existing_user = cursor.fetchone()
        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
            
            cursor.execute(find_user_by_id(id))
            username = cursor.fetchone()
            
            cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{id}'")
            profile_pic = cursor.fetchall()
            
            cnx.close()

        # print(profile_pic)        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()    
            cursor.execute("SELECT * FROM users")
            all_user = cursor.fetchall()
            # print(all_user)
        if profile_pic ==[]:
            profile = "user.png"
        else:
            profile = profile_pic[0][0]
        
        users = []
        posts = []
        interest = []
        inter = []
        interest_return =[]

        for pic in all_user:
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
                
                cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
                existing_user = cursor.fetchone()
 
            if pic[1] != existing_user[1]:
                if pic[10] == 'Male':

                    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                        cursor=cnx.cursor()
                                    
                        cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{pic[0]}'")
                               
                        picture = cursor.fetchall()
                                    
                    if pic[1] in users:
                        continue
                    else:
                                    # print(pic[0])
                        print('-----------------------')

                        if picture != []:
                            users.append(pic[1])
                            posts.append(picture[0])

    return render_template('public/profile.html',notification=existing_user[-2],existing_user=existing_user,notification_numb=existing_user[-1],posts=posts,profile=profile, users=users, user=session["USER"],username=username, isIndex=True, madness=True)

@app.route('/gen_female',methods=['GET','POST'])
@is_logged_in
def gen_female():

    if session.get('USER',None) is not None:

        id=session.get("USER")

        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
                
            cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
            existing_user = cursor.fetchone()
        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
            
            cursor.execute(find_user_by_id(id))
            username = cursor.fetchone()
            
            cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{id}'")
            profile_pic = cursor.fetchall()
            
            cnx.close()

        # print(profile_pic)        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()    
            cursor.execute("SELECT * FROM users")
            all_user = cursor.fetchall()
            # print(all_user)
        if profile_pic ==[]:
            profile = "user.png"
        else:
            profile = profile_pic[0][0]
        
        users = []
        posts = []
        interest = []
        inter = []
        interest_return =[]

        for pic in all_user:
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
                
                cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
                existing_user = cursor.fetchone()
 
            if pic[1] != existing_user[1]:
                if pic[10] == 'Female':

                    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                        cursor=cnx.cursor()
                                    
                        cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{pic[0]}'")
                               
                        picture = cursor.fetchall()
                                    
                    if pic[1] in users:
                        continue
                    else:
                                    # print(pic[0])
                        print('-----------------------')

                        if picture != []:
                            users.append(pic[1])
                            posts.append(picture[0])

    return render_template('public/profile.html',notification=existing_user[-2],notification_numb=existing_user[-1],existing_user=existing_user,posts=posts,profile=profile, users=users, user=session["USER"],username=username, isIndex=True, madness=True)

@app.route('/gen_bi',methods=['GET','POST'])
@is_logged_in
def gen_bi():

    if session.get('USER',None) is not None:

        id=session.get("USER")

        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
                
            cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
            existing_user = cursor.fetchone()
        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
            
            cursor.execute(find_user_by_id(id))
            username = cursor.fetchone()
            
            cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{id}'")
            profile_pic = cursor.fetchall()
            
            cnx.close()

        # print(profile_pic)        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()    
            cursor.execute("SELECT * FROM users")
            all_user = cursor.fetchall()
            # print(all_user)
        if profile_pic ==[]:
            profile = "user.png"
        else:
            profile = profile_pic[0][0]
        
        users = []
        posts = []
        interest = []
        inter = []
        interest_return =[]

        for pic in all_user:
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
                
                cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
                existing_user = cursor.fetchone()
 
            if pic[1] != existing_user[1]:
                if pic[10] == 'Bisexual':

                    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                        cursor=cnx.cursor()
                                    
                        cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{pic[0]}'")
                               
                        picture = cursor.fetchall()
                                    
                    if pic[1] in users:
                        continue
                    else:
                                    # print(pic[0])
                        print('-----------------------')

                        if picture != []:
                            users.append(pic[1])
                            posts.append(picture[0])

    return render_template('public/profile.html',notification=existing_user[-2],notification_numb=existing_user[-1],existing_user=existing_user,posts=posts,profile=profile, users=users, user=session["USER"],username=username, isIndex=True, madness=True)

@app.route('/gen_all',methods=['GET','POST'])
@is_logged_in
def gen_all():

    if session.get('USER',None) is not None:

        id=session.get("USER")

        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
                
            cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
            existing_user = cursor.fetchone()
        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
            
            cursor.execute(find_user_by_id(id))
            username = cursor.fetchone()
            
            cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{id}'")
            profile_pic = cursor.fetchall()
            
            cnx.close()

        # print(profile_pic)        
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()    
            cursor.execute("SELECT * FROM users")
            all_user = cursor.fetchall()
            # print(all_user)
        if profile_pic ==[]:
            profile = "user.png"
        else:
            profile = profile_pic[0][0]
        
        users = []
        posts = []
        interest = []
        inter = []
        interest_return =[]

        for pic in all_user:
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
                
                cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
                existing_user = cursor.fetchone()
 
            if pic[1] != existing_user[1]:
                # if pic[10] == 'Bisexual':

                    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                        cursor=cnx.cursor()
                                    
                        cursor.execute(f"SELECT `picture` FROM `pictures` WHERE `user_id`='{pic[0]}'")
                               
                        picture = cursor.fetchall()
                                    
                    if pic[1] in users:
                        continue
                    else:
                                    # print(pic[0])
                        print('-----------------------')

                        if picture != []:
                            users.append(pic[1])
                            posts.append(picture[0])

    return render_template('public/profile.html',notification=existing_user[-2],notification_numb=existing_user[-1],existing_user=existing_user,posts=posts,profile=profile, users=users, user=session["USER"],username=username, isIndex=True, madness=True)

@app.route("/logout")
@is_logged_in
def logout():
    session.pop('user',None)
    session.clear()
    res = make_response("Cookie Removed")
    res.set_cookie('foo', 'bar', max_age=0)
    return redirect(url_for('login'))


@app.route('/update',methods=['GET','POST'])
@is_logged_in
def update():
    form = UpdateAccountForm()

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM `users`")
        items = cursor.fetchall()
    
    arr = []
    for i in items:
        if i[13] is not None:
            arr.append(i[13])

    print(arr)   
    
    interest = form.interest.data 
    age = form.age.data
    bio = form.bio.data
    gender = form.gender.data
    sexualPreference =form.sexualPreference.data

    print(sexualPreference)
    try:
        if request.method == 'POST':
            if(str(age).isdigit()):
                if age >= 21:
                    if age <= 85:
                        if check_interest(interest):
                            if check_bio(bio):
                                if check_gender(gender):
                                    if check_sexualP(sexualPreference):
                                        if user_update(form) == True:
                                            if form.picture.data:
                                                picture_file = save_picture(form.picture.data)
                                                return redirect(url_for('profile'))
                                            else:
                                                flash('You need to upload a profile picture/upda', 'danger')
                                                return render_template('public/update_profile.html',form=form, isUpdate=True)
                                        else:
                                            flash('Something went wrong.' 'danger')
                                            return render_template('public/update_profile.html',form=form, isUpdate=True)
                                    else:
                                        flash('Sexual preference selection is incorrect.', 'danger')
                                        return render_template('public/update_profile.html',form=form, isUpdate=True)        
                                else:
                                    flash('Gender selection is incorrect.', 'danger')
                                    return render_template('public/update_profile.html',form=form, isUpdate=True)
                            else:
                                flash('Your biography needs to be a minimum of four characters long, please try again.', 'danger')
                                return render_template('public/update_profile.html',form=form, isUpdate=True)
                        else:
                            flash('You need begin your interests with # (Hashtag)', 'danger')
                            return render_template('public/update_profile.html',form=form, isUpdate=True)
                    else:
                        flash('You are too old, please try again in your next lifetime.', 'danger')
                        return render_template('public/update_profile.html',form=form, isUpdate=True)    
                else:
                    flash('You are too young, please try again in the near future.', 'danger')
                    return render_template('public/update_profile.html',form=form, isUpdate=True)
            else:
                flash('Age needs to be a valid number between 21 and 85 years, please try again', 'danger')
                return render_template('public/update_profile.html',form=form, isUpdate=True)
        else:
            if check_where() == True:
                flash('That page can only be accessed on first time sign in.', 'danger')
                return redirect(url_for('profile'))
            else:
                return render_template('public/update_profile.html',arr=arr,form=form, isUpdate=True)
    except:
        flash("The picture is of invalid format or too big of a size to upload, please upload a file ending with either .jpg, .png or .peg which is not greater than 2MB in size and try again.",'danger')
        return render_template('public/update_profile.html',form=form, isUpdate=True)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)

    #This function(splitext) returns two values,the file name without,
    #the extension and it returns the extension itself,below we grab
    #both values
    # f_name,f_ext = os.path.splitext(form_picture.filename)
    
    #on this one we grab only the extension
    _,f_ext= os.path.splitext(form_picture.filename)


    #her we concanating the extesion with the randon hex to create,
    #a new name for the uploaded image
    picture_fn = random_hex + f_ext

    #getting the root path
    picture_path = os.path.join(app.root_path,'static/img',picture_fn)


    output_size = (125,125)

    i = Image.open(form_picture)
    i.thumbnail(output_size)

    id=session.get("USER")
    pic_id =secrets.token_urlsafe() 
    
    # with sqlmgr(user='root',pwd='',db='Matcha') as cnx:
        # cursor=cnx.cursor()
        
        # cursor.execute(f"SELECT * FROM `pictures` WHERE `user_id`='{id}'")
        # picture = cursor.fetchone()
    
    
    
    
    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
    
        # cursor.execute(find_user_by_id(id))
        # current_user = cursor.fetchone()

        # cursor.execute(find_email_and_username_by_id(id))
        # email_and_username_by_id = cursor.fetchone()
        
        cursor.execute(f"SELECT COUNT(`picture`) FROM `pictures` WHERE `user_id`='{id}'")
        picture = cursor.fetchone()
        
        # print(current_user[0])
        # SELECT `email`,`username` FROM users WHERE `user_id`='{id}'
        
        print(id)
        
        # for k in picture:
        print(f"This is the length {picture}")
        print(f"just checking {len(picture)}")
            
        if picture[0] <= 6:
            cursor.execute(
                f"""INSERT INTO 
                `pictures`(`pictures_id`,`user_id`,`picture`)
                VALUES('{pic_id}','{id}','{picture_fn}')
                """
            )
        else:
            flash('You have reached a limit of the number of picture you can upload','danger')
        
        cnx.commit()
        
        # cursor.execute(f"INSERT INTO `pictures`(picture) VALUES('{picture_fn}') WHERE `user_id`='{id}'")
    
    # current_user = find_blog_post(id)
    print(picture_fn)
    # current_post = find_id(id)
    # INSERT INTO `pictures`(pictures_id,user_id,picture) VALUES('NOTHING',(SELECT user_id FROM users WHERE username='mapula'),'just run');
    
    # current_post.update_one(push__pictures=picture_fn)
    # current_post['pictures'].append(picture_fn)
    # if len(current_user['pictures']) < 7:
    
    # push_pictures_blog_post(id,picture_fn)
    # else:
        # flash("Sorry you have reach a limit on number of pictures you can uplaod",'danger')
        # return redirect(url_for('profile'))
    # for post in current_post:
    #     print(post.content)

    # current_post.update_one(push_pictures=picture_fn)



    # print(current_post.content)SELECT * FROM `pictures` WHERE 

    print(len(picture_path))

    i.save(picture_path)

    # picture_path = os.path.join(app.config['IMAGE_UPLOADS'],filename)
    return picture_fn
# @app.route('/numbers',methods=['GET'])
# def pagination():
#     print(users_pagination())

    return render_template('public/profile.html')


@app.route("/account",methods=['POST','GET'])
@is_logged_in
def account():
    form=UploadsForm()

    id=session.get("USER")
    username = form.username.data
    email = form.email.data
    interest = form.interest.data 
    age = form.age.data
    bio = form.bio.data
    gender = form.gender.data
    city = form.city.data
    sexualPreference = form.sexualPreference.data

    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
                
        cursor.execute(f"SELECT `city` FROM `location` WHERE `user_id`= '{id}'") 
        current_location = cursor.fetchall()
    print(current_location)
    
    try:
        if check_where():
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
        
                cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
                existing = cursor.fetchone()
    
            notification = existing[-2]
            # existing_blog_post = find_blog_post(id_)
            with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
                cursor=cnx.cursor()
        
                cursor.execute(find_user_by_id(id))
                existing_user = cursor.fetchone()

            if request.method == 'POST':
        
                if check_username(username):
                    upd_username(form)
                else:
                    flash('The username field must be between 2 to 30 characters long and can be AlphaNumeric, please try again', 'danger')
                if check_mail(email):
                    upd_email(form)
                else:
                    flash('The email address is invalid, please try again','danger')
                if str(age).isdigit():
                    if age >= 21:
                        if age <= 85:
                            upd_age(form)
                        else:
                            flash('You are too old, please try again in your next lifetime.', 'danger')
                    else:
                        flash('You are too young, please try again in the near future.', 'danger')    
                else:
                    flash('Age needs to be a valid number between 21 and 85 years, please try again', 'danger')    
                if check_interest(interest):
                    upd_interest(form)
                else:
                    flash('You need begin your interests with # (Hashtag)', 'danger')
                if check_bio(bio):
                    upd_bio(form)
                else:
                    flash('Your biography needs to be a minimum of four characters long, please try again.', 'danger')
                if check_gender(gender):
                    upd_gender(form)
                else:
                    flash('Gender selection is incorrect.', 'danger')
                if check_sexualP(sexualPreference):
                    upd_sexual(form)
                else:
                    flash('Sexual preference selection is incorrect.', 'danger')
                if check_first_last_name(city):
                    upd_city(form)
                else:
                    flash('City preference is incorrect.', 'danger')
                if form.picture.data:
                    picture_file = save_picture(form.picture.data)
        else:
            flash("You need to fill in all your information on this page before you are granted access to any page within the app.",'danger')
            return redirect(url_for('update'))   
    except:
        flash("The picture is of invalid format or too big of a size to upload, please upload a file ending with either .jpg, .png or .peg which is not greater than 2MB in size and try again.",'danger')

    return render_template('public/account.html',notification_numb=existing[-1],form=form,existing_user=existing_user[0],notification=notification,isHere=True)


@app.route("/post/new",methods=['GET','POST'])
def new_post():
    form= PostForm()
    if form.validate_on_submit():
        flash('Your Post has been created','success')
        return redirect(url_for('profile'))

    return render_template('public/create_post.html',title='Post',form=form)


@app.route("/post/<string:post_id>")
def post(post_id):
    
    user =post_id

    if user != 'tagify.css':
        # print(f"{user}^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^))))))))))))))))))))))))))))))))0")
        # id = str(post_id)
        # print(id)

        id = session.get("USER")

        



        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()

            cursor.execute(f"SELECT * FROM `users` WHERE `user_id`= '{id}'") 
            existing_user = cursor.fetchone()



        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()

            cursor.execute(f"SELECT * FROM `users` WHERE `username`= '{user}'")
            check_token = cursor.fetchone()

        # with sqlmgr(user="root", pwd="",db='Matcha') as cnx:
        #     cursor = cnx.cursor()

        #     cursor.execute(f"SELECT * FROM `users` WHERE user_id ='{user}'")
        #     users = cursor.fetchone()

        # for i in users:

        # print(f"%%%%%%%%%%%%%%%%%%%%%{check_token}")
        post=check_token
        token=check_token
        if post is not None:
            print(f"{post[0]} check this works")
            with sqlmgr(user="root", pwd="",db='Matcha') as cnx:
                cursor = cnx.cursor()

                cursor.execute(f"SELECT * FROM `location` WHERE user_id ='{post[0]}'")
                city = cursor.fetchone()


            with sqlmgr(user="root", pwd="",db='Matcha') as cnx:
                cursor = cnx.cursor()

                cursor.execute(f"SELECT * FROM `pictures` WHERE user_id ='{token[0]}'")
                picture = cursor.fetchall()


            author=check_token

            # print(picture[])

            # print(check_token)

            # id = post['_id']

            # author = find_blog_post(id)

            # print(type(author))
            # for pic in author:
            # print(pic)




        return render_template('public/post.html',picture=picture,post=post,city=city,author=author,notification=existing_user[-2],notification_numb=existing_user[-1])
    else:
        pass



@app.route("/post/<string:post_id>/update",methods=['GET','POST'])
def update_post(post_id):
    id = str(post_id)
    post = find_blog_post(id)

    print(post['author'])
    # print(session["USER"])
    # return redirect(request.url)
    if str(post['author']) != session["USER"]:
        abort(403)
    form = PostForm()
    author=str(post['author'])
    
    return render_template('public/post.html',form=form,post=post,current_user=session["USER"],author=author )

@app.route("/post/<string:post_id>/delete",methods=['POST',])
def delete_post(post_id):
    # id = str(post_id)
    id = post_id
    post = find_post(id)
    id = post['author']
    picture = post_id
    delete_existing_post(id,picture)
    # print(selected)

    # post = find_blog_post(id)
    # print(post)

    # if str(post['author']) != session["USER"]:
    #     abort(403)
    # delete_existing_post(id)
    # flash('Your post has been deleted!','success')
    # return redirect(request.url)
    return redirect(url_for('profile'))


@app.route("/hash_tag/<post_id>",methods=['POST','GET'])
def hash_tag(post_id):

    id=session.get("USER")
    tags = post_id
    tag = request.url
    
    with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM `users` WHERE `user_id`='{id}'")
        existing_user = cursor.fetchone()

    # with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
    #     cursor=cnx.cursor()
    #     cursor.execute(f"SELECT * FROM `users` WHERE `Interest`='#{post_id}'")
    #     hasing = cursor.fetchone()

    # print(f"This is the value{hasing}")


    
    # print(existing_user)
    liked = existing_user[-2]

    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM `users`")
        all_existing_user = cursor.fetchall()

    
    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
        cursor=cnx.cursor()
        cursor.execute(f"SELECT * FROM `pictures`")
        all_existing_blog_post = cursor.fetchall()


    # liked_number = len(liked)
    # all_existing_blog_post
    # all_existing_user = all_existing_users()
    users = []
    pic=[]
 
   
    
    user_k = existing_user[13].split(',')
    for name in all_existing_user:
        # print(name[1])
        # print(existing_user[1])
          
        users_i = name[13].split(',')
        for i in users_i:
            pic.append(i)

        # if name[1] != existing_user[1]:
        #     # print(name[1])
        #   )

    for k in pic:
        if k == tags:
            print(k)
    
    # print(pic)
    #             #     if name in users:
    #             #         continue
    #             #     else:
    #             #         print(name)
    #             #         users.append(name)
    #             #         # print(name)

    # print(users)
    
    # with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
        # cursor=cnx.cursor()
        # cursor.execute(f"SELECT * FROM `pictures` WHERE `user_id`='{id}'")
        # ps = cursor.fetchall()
    # for i in users:
        # print(ps)
        

    return render_template('public/landing_page.html',users=users,existing_user=existing_user)
