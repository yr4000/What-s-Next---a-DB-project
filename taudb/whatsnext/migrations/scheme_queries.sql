-- This is the old version of places
-- CREATE TABLE places_old (
--     `id` INT NOT NULL AUTO_INCREMENT,
--     `google_id` VARCHAR(50) UNIQUE NOT NULL,
--     `name` VARCHAR(255) NOT NULL,
--     `rating` FLOAT DEFAULT NULL,
--     `vicinity` VARCHAR(255) DEFAULT NULL,
--     `latitude` FLOAT(10 , 7 ) NOT NULL,
--     `longitude` FLOAT(10 , 7 ) NOT NULL,
--     PRIMARY KEY (`id`),
--     KEY `idx_google_id` (`google_id`),
--     KEY `idx_name` (`name`),
--     KEY `idx_rating` (`rating`),
--     KEY `idx_address` (`vicinity`),
--     KEY `idx_latitude` (`latitude`),
--     KEY `idx_longitude` (`longitude`)
-- )  ENGINE=INNODB DEFAULT CHARSET=UTF8;


CREATE TABLE categories (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;

INSERT INTO categories (`name`) VALUES ('lodging');
INSERT INTO categories (`name`) VALUES ('restaurant');
INSERT INTO categories (`name`) VALUES ('bar');
INSERT INTO categories (`name`) VALUES ('museum');

-- This is the old version of places_categories
-- CREATE TABLE places_categories_old (
--     `id` INT NOT NULL AUTO_INCREMENT,
--     `place_id` INT NOT NULL,
--     `category_id` INT NOT NULL,
--     PRIMARY KEY (`id`),
--     CONSTRAINT `fgn_place_id` FOREIGN KEY (`place_id`) REFERENCES places (`id`),
--     CONSTRAINT `fgn_category_id` FOREIGN KEY (`category_id`) REFERENCES categories (`id`),
-- 	UNIQUE KEY `place_id_category_id` (`place_id`,`category_id`)
-- )  ENGINE=INNODB DEFAULT CHARSET=UTF8;


CREATE TABLE reviews (
    `id` INT NOT NULL AUTO_INCREMENT,
    `place_id` INT NOT NULL,
    `author` VARCHAR(255) NOT NULL,
    `rating` FLOAT default 0,
    `date` DATE DEFAULT NULL,
    `text` TEXT NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_review_place_id` (`place_id`),
    CONSTRAINT `fgn_place_id_reviews` FOREIGN KEY (`place_id`) REFERENCES places (`id`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;


CREATE TABLE places (
    `id` INT NOT NULL AUTO_INCREMENT,
    `google_id` VARCHAR(50) UNIQUE NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `rating` FLOAT DEFAULT NULL,
    `vicinity` VARCHAR(255) DEFAULT NULL,
    `latitude` MEDIUMINT NOT NULL,
    `longitude` MEDIUMINT NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_google_id` (`google_id`),
    KEY `idx_name` (`name`),
    KEY `idx_rating` (`rating`),
    KEY `idx_address` (`vicinity`),
    KEY `idx_latitude` (`latitude`),
    KEY `idx_longitude` (`longitude`)
)  ENGINE=MyISAM DEFAULT CHARSET=UTF8;

-- TODO: MyISAM does NOT support foreign keys, need to recreate this table
CREATE TABLE places_categories (
    `id` INT NOT NULL AUTO_INCREMENT,
    `place_id` INT NOT NULL,
    `category_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fgn_pc2_place_id` FOREIGN KEY (`place_id`) REFERENCES places (`id`),
    CONSTRAINT `fgn_pc2_category_id` FOREIGN KEY (`category_id`) REFERENCES categories (`id`),
	UNIQUE KEY `place_id_category_id` (`place_id`,`category_id`)
)  ENGINE=MyISAM DEFAULT CHARSET=UTF8;


CREATE TABLE search_popularity
(
	search_id INT NOT NULL AUTO_INCREMENT,
  po0pularity INT NOT NULL,
  CHECK (popularity>0),
  PRIMARY KEY (search_id)
)

#TODO we should make sure it is also at least 1
ALTER TABLE search_popularity
ADD search_size INT


CREATE TABLE searches_places
(
	search_id INT NOT NULL,
    place_id INT NOT NULL
)

# TODO remember to delete those values
INSERT INTO search_popularity
VALUES (1,5)

INSERT INTO searches_places
VALUES (1,1)