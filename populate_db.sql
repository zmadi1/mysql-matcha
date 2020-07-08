-- USE Matcha;
USE test;

CREATE TABLE IF NOT EXISTS `data` 
(
  `id`         bigint(20) NOT NULL      AUTO_INCREMENT,
  `datetime`   VARCHAR(20)  NULL          ,
  `channel`    int(11)                  DEFAULT NULL,
  `value`      float                    DEFAULT NULL,

  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `users` 
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
            PRIMARY KEY(user_id));

DELIMITER $$
CREATE PROCEDURE generate_data()
BEGIN
  DECLARE i INT DEFAULT 0;
  WHILE i < 500 DO
    INSERT INTO `users` (`user_id`,`username`,`firstname`, `lastname`, `email`, `password`, `age`, `bio`, `registered`, `gender`, `sexualPreference`, `AccountVerification`, `Interest`) VALUES (
      concat(char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97,char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97))),
      concat(char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97))),
      concat(char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97))),
      concat(char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97),char(round(rand()*25)+97))),
      CONCAT(SUBSTRING(MD5(UUID()),1,12),'@yeah.com'),
      "$2b$12$GD3fC/25yPVH4BXy6155G.NMB79H1AolVAmyUK8UX.uamAtyu/ynC",
      25,
      "The truth can only be foung in one place, the code...it never lies.",
      1,
      
      ROUND(RAND()*1000,2),
      1
    );
    SET i = i + 1;
  END WHILE;
END$$
DELIMITER ;

CALL generate_data();


DROP PROCEDURE generate_data;


-- DROP TABLE IF EXISTS `users`;


-- CREATE TABLE IF NOT EXISTS `pictures`(
--                 pictures_id VARCHAR(100) ,
--                 user_id VARCHAR(200) NOT NULL,
--                 picture VARCHAR(100), 
--                 PRIMARY KEY(pictures_id),
--                 FOREIGN KEY(user_id) REFERENCES `users`(user_id));

-- CREATE TABLE IF NOT EXISTS `liked`(
--                 liked_id VARCHAR(100) ,
--                 user_id VARCHAR(200) NOT NULL,
--                 username VARCHAR(100), 
--                 PRIMARY KEY(liked_id),
--                 status VARCHAR(100) NOT NULL,
--                 epoch VARCHAR(250) NOT NULL,
--                 FOREIGN KEY(user_id) REFERENCES `users`(user_id));

-- CREATE TABLE IF NOT EXISTS `likes`(
--                 likes_id VARCHAR(100) ,
--                 user_id VARCHAR(200) NOT NULL,
--                 username VARCHAR(100), 
--                 PRIMARY KEY(likes_id),
--                 status VARCHAR(100) NOT NULL,
--                 epoch VARCHAR(250) NOT NULL,
--                 FOREIGN KEY(user_id) REFERENCES `users`(user_id));

