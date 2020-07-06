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

                    with sqlmgr(user="root",pwd="",db="Matcha") as cnx:
                        cursor=cnx.cursor()
                        cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS `location`(
                        gis_id VARCHAR(100) ,
                        user_id VARCHAR(200) NOT NULL,
                        lat FLOAT NOT NULL,
                        lon FLOAT NOT NULL, 
                        PRIMARY KEY(gis_id),
                        FOREIGN KEY(user_id) REFERENCES `users`(user_id)
                        )
                        """
                        )
                        cnx.commit()
user_id
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

                            cursor.execute(f"""INSERT INTO `location`(`gis_id`,`user_id`,`lat`,`lon`)  VALUES("{gis_id}","{existing_user[0]}","{req['lat']}","{req['long']}")""")
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