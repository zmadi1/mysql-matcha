import mysql.connector

# s = URLSafeTimedSerializer('thisissecret')
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
    

    #    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `messages`
    #         (
    #             message_id VARCHAR(200) NOT NULL,
    #             user_id VARCHAR(200) NOT NULL,
    #             message TEXT NOT NULL,
    #             username VARCHAR(100) NOT NULL,
    #             epoch VARCHAR(250) NOT NULL,  
    #             PRIMARY KEY(message_id),
    #             FOREIGN KEY(user_id) REFERENCES `users`(user_id)
    #         )""")
    try:
        cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `liked`(
            liked_id VARCHAR(100) ,
            user_id VARCHAR(200) NOT NULL,
            username VARCHAR(100), 
            PRIMARY KEY(liked_id),
            status VARCHAR(100) NOT NULL,
            epoch VARCHAR(250) NOT NULL,
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
            status VARCHAR(100) NOT NULL,
            epoch VARCHAR(250) NOT NULL,
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
    except mysql.connector.errors.IntegrityError as err:
        print(err)
        raise