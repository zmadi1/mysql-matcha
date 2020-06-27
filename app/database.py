import mysql.connector

from flask import jsonify,abort,make_response,render_template,url_for,flash,g, redirect,session,request,make_response
from app import app
from flask_bcrypt import Bcrypt
from datetime import datetime
import secrets
import os
from flask_paginate import Pagination,get_page_parameter
from flask_mail import Mail,Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

bcrypt = Bcrypt(app)
# mail = Mail(app)


s = URLSafeTimedSerializer('thisissecret')
class sqlmgr:
    #initialize parameters for connection estaablishment
    def __init__(self,user,pwd,db,host='localhost',IgnoreError=False):
        self.user=user
        self.pwd=pwd
        self.host=host
        self.db=db
        self.IgnoreError=IgnoreError
    #establishes connection to database
    def __enter__(self):
        self.cnx = mysql.connector.connect(user=self.user,password=self.pwd,host=self.host,database=self.db)
        return self.cnx
    #close database connection
    def __exit__(self,ex_type,ex_value,traceback):
        self.cnx.close()
        if ex_type is not None:
            return self.IgnoreError


#query user_id
def find_user_id(username):
    user = f"SELECT `user_id` FROM users WHERE `username`='{username}'"
    return user

# def find_user_by_id(id):
#     user = f"SELECT `username` FROM users WHERE `user_id`='{id}'"
#     return user
#query username
def find_username(username):
    
    user = f"SELECT `username` FROM  users WHERE  `username`='{username}'"
    return user

def find_registered(username):
    
    user = f"SELECT `registered` FROM  users WHERE  `username`='{username}'"
    return user

#query email
def find_email(email):
    user = f"SELECT `email` FROM  users WHERE  `username`='{email}'"
    return user

#query password
def find_password(username):
    user = f"SELECT `password` FROM  users WHERE  `username`='{username}'"
    return user

#query user_id
def find_age_and_bio(username):
    user = f"SELECT `age`,`bio` FROM users WHERE `user_id`='{username}'"
    return user

#query user_id
def find_email_and_username_by_id(id):
    user = f"SELECT `email`,`username` FROM users WHERE `user_id`='{id}'"
    return user

#search using user_id
def find_user_by_id(id): 
    user = f"SELECT `username` FROM users WHERE `user_id`='{id}'"
    return user

def count_user(username):
    user= f"SELECT COUNT('username') FROM users WHERE `username`='{username}'"
    return user


def count_email(email):
    
    user= f"SELECT COUNT('email') FROM users WHERE `email`='{email}'"
    return user


# age_update(form,id)
# bio_update(form,id)
# gender_update(form,id)
# sexualPreference_update(form,id)
# registered_update(id)
# interest_update(form,id)

def age_update(username,age):
    user = f"UPDATE users SET `age` = '{age}' WHERE `username`='{username}'"
    return user

def bio_update(username,bio):
    user = f"UPDATE users SET `bio` = '{bio}' WHERE `username`='{username}'"
    return user

def sexualPreference_update(username,sexualPreference):
    user = f"UPDATE users SET `sexualPreference` = '{sexualPreference}' WHERE `username`='{username}'"
    return user

def gender_update(username,gender):
    user = f"UPDATE users SET `gender` = '{gender}' WHERE `username`='{username}'"
    return user

def interest_update(username,interest):
    user = f"UPDATE users SET `Interest` = '{interest}' WHERE `username`='{username}'"
    return user

def registered_update(username):
    user = f"UPDATE users SET `registered`=TRUE WHERE `username`='{username}'"
    return user 
  




def user_update(form):
    id = session["USER"]
    
    interest = form.interest.data 
    age = form.age.data
    bio = form.bio.data
    gender = form.gender.data
    sexualPreference =form.sexualPreference.data 

    try:
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
            
            cursor.execute(find_user_by_id(id))
            
            username = cursor.fetchone()

            
            cursor.execute(find_age_and_bio(id))
            user = cursor.fetchone()
            
            
            print(user)
            
    
     
            if user[0] != None and user[1] != None:
                return True
            else:
                if form.validate_on_submit():
                    cursor.execute(f"UPDATE users SET `age` = '{age}' WHERE `username`='{username[0]}'")
                    cursor.execute(f"UPDATE users SET `bio` = '{bio}' WHERE `username`='{username[0]}'")
                    # cursor.execute(f"UPDATE users SET `gender` = '{gender}' WHERE `username`='{username[0]}'")
                    cursor.execute(f"UPDATE users SET `sexualPreference` = '{sexualPreference}' WHERE `username`='{username[0]}'")
                    cursor.execute(f"UPDATE users SET `gender` = '{gender}' WHERE `username`='{username[0]}'")
                    cursor.execute(f"UPDATE users SET `Interest` = '{interest}' WHERE `username`='{username[0]}'")
                    cursor.execute(f"UPDATE users SET `registered`=TRUE WHERE `username`='{username[0]}'")
                    cnx.commit()
                return True
    except mysql.connector.Error as err:
        print('*****************************')
        flash('An erro has happend','danger')
        print(err)

def user_login(form):

    # email = form.email.data 
    username = form.username.data
    # firstname = form.firstname.data
    # lastname = form.lastname.data
    password =form.password.data 
    # bcrypt.generate_password_hash(form.password.data).decode('utf-8')

    try:
        with sqlmgr(user="root",pwd="",db='Matcha') as cnx:
            cursor=cnx.cursor()
            
            # with sqlmgr(user='root',pwd='',db='Matcha') as cnx:
            # cursor=cnx.cursor()
            # cursor.execute('USE Matcha')
            # cursor.execute(find_username(username))
            
            cursor.execute(find_username(username))
            user = cursor.fetchone()
            cursor.execute(find_password(username))
            passwd = cursor.fetchone()
            cursor.execute(find_registered(username))
            registered = cursor.fetchone()
            cursor.execute(find_user_id(username))
            user_id = cursor.fetchone()
            
            # print(user[0])
            # print(passwd[0])
            # print(registered[0])
            # print(bcrypt.check_password_hash(passwd[0] ,password))
            if user[0] == username:
                if bcrypt.check_password_hash(passwd[0] ,password) == True:
                    # print('*****************************it did work!!!!!!!!!!!!!!!!!!!!')
                    
                    
                    # print(existing_user['username'])
                    # print(existing_user['_id'])
                    
                    # print('*****************************it did work!!!!!!!!!!!!!!!!!!!!')
                    session["USER"] = str(user_id[0])
                    # print(user_id)
                    # print(type(session["USER"]))
                    # session["USERNAME"]=username
                    # print(session.get('USER'))
                    
                    # print('*****************************it did work!!!!!!!!!!!!!!!!!!!!')
                    # print(registered[0])
                    if registered[0] == 1:
                        # print('Did you see this!!!!!!!!')
                        return  True
                    else:
                        # print('*****************************it did not work!!!!!!!!!!!!!!!!!!!!')
                        return False
                else:
                    flash('Please check your password or email and try again','danger')
                    return redirect(request.url)           
            else:
                flash('Sorry the user doesnt\'t exist please try again','danger')
                return redirect(request.url)
        # cnx.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(err)
        
    return
def resetP(form):
    email = form.email.data

def create_users(form):
    
    user_id= secrets.token_urlsafe()
    pic_id =secrets.token_urlsafe()

    email = form.email.data 
    username = form.username.data
    firstname = form.firstname.data
    lastname = form.lastname.data
    password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

    token = s.dumps(email,salt='email-confirm')

    print(token)

    try:
        with sqlmgr(user="root",pwd="",db='') as cnx:
            cursor=cnx.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS Matcha")
            cnx.commit()
            cursor.close()
    except mysql.connector.Error as err:
        print(err)

    with sqlmgr(user='root',pwd='',db='Matcha') as cnx:
        cursor=cnx.cursor()
        # cursor.execute('USE Matcha')

        try:
            cursor.execute(
           """CREATE TABLE IF NOT EXISTS `users` 
            (
            user_id VARCHAR(200) NOT NULL,
            username VARCHAR(20) NOT NULL UNIQUE,
            firstname VARCHAR(20) NOT NULL,
            lastname VARCHAR(20) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password TEXT NOT NULL,
            age INT,
            bio TEXT ,
            categories TEXT,
            registered BOOLEAN,
            gender VARCHAR(20),
            sexualPreference VARCHAR(20),
            AccountVerification BOOLEAN,
            Interest TEXT,
            tokenCode VARCHAR(200),
            notification INT,
            notification_numb INT,
            PRIMARY KEY(user_id)
            )
           """
            )
            cnx.commit()
        except mysql.connector.errors.IntegrityError as err:
            flash('The table was not created','danger')
        
        try:
            cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `pictures`(
                pictures_id VARCHAR(100) ,
                user_id VARCHAR(200) NOT NULL,
                picture VARCHAR(100), 
                PRIMARY KEY(pictures_id),
                FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                )
                """
                )
            cnx.commit()
        except mysql.connector.errors.IntegrityError as err:
            print(err)
            raise
        
        try:
            cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `liked`(
                liked_id VARCHAR(100) ,
                user_id VARCHAR(200) NOT NULL,
                username VARCHAR(100), 
                PRIMARY KEY(liked_id),
                FOREIGN KEY(user_id) REFERENCES `users`(user_id))
            """
            )
            cnx.commit()
        except mysql.connector.errors.IntegrityError as err:
            print(err)
            raise
        
        try:
            cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `likes`(
                likes_id VARCHAR(100) ,
                user_id VARCHAR(200) NOT NULL,
                username VARCHAR(100), 
                PRIMARY KEY(likes_id),
                FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                )
            """
            )
            cnx.commit()
        except mysql.connector.errors.IntegrityError as err:
            print(err)
            raise
        
        try:
            
            cursor.execute(count_user(username))
            user_number = cursor.fetchone()
            
            cursor.execute(count_email(email))
            email_number = cursor.fetchone()
            
            print(f'Here we are checking {token}')
            session["TOKEN"] = token
            print('This is a newly created session')
            print(session.get("TOKEN"))
            if user_number[0] != 1:
                
                if email_number[0] != 1:

                    print(session.get("TOKEN"))
                    cursor.execute(
                    f"""INSERT INTO  
                    `users`(`user_id`,`username`,`firstname`,`lastname`,`email`,`password`,`registered`,`AccountVerification`,`tokenCode`, `notification`,`notification_numb`)
                    VALUES('{user_id}','{username}','{firstname}','{lastname}','{email}','{password}',FALSE,FALSE,'{token}',0,0)""")
                    cnx.commit()
                    return True
                else:
                    flash('The email have been taken,please try a different one','danger')
                    return False
            else:
                flash('The username have been taken,please try a different one','danger')
        except:
            pass
            # flash('The username or the email have been taken,please try a different one','danger')
        cursor.close()
