CREATE TABLE categories (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;

INSERT INTO categories (`name`) VALUES ('hotel');
INSERT INTO categories (`name`) VALUES ('restaurant');
INSERT INTO categories (`name`) VALUES ('bar');
INSERT INTO categories (`name`) VALUES ('museum');


CREATE TABLE reviews (
    `id` INT NOT NULL AUTO_INCREMENT,
    `place_id` INT NOT NULL,
    `author` VARCHAR(255) NOT NULL,
    `rating` FLOAT default 0,
    `date` DATE DEFAULT NULL,
    `text` TEXT NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_review_place_id` (`place_id`)
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
    KEY `idx_rating` (`rating`),
    KEY `idx_latitude` (`latitude`),
    KEY `idx_longitude` (`longitude`),
    FULLTEXT KEY `name` (`name`)
)  ENGINE=MyISAM DEFAULT CHARSET=UTF8;


CREATE TABLE places_categories (
    `place_id` INT NOT NULL,
    `category_id` INT NOT NULL,
    PRIMARY KEY (`place_id`, `category_id`),
    CONSTRAINT `fgn_pc3_category_id` FOREIGN KEY (`category_id`) REFERENCES categories (`id`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;


CREATE TABLE choices (
	choice_id INT NOT NULL AUTO_INCREMENT,
  popularity INT NOT NULL,
  PRIMARY KEY (choice_id),
  CHECK (popularity>0),
  KEY `idx_popularity` (`popularity`)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;


CREATE TABLE choices_places (
  `choice_id` int NOT NULL,
  `place_id` int NOT NULL,
  PRIMARY KEY (`choice_id`,`place_id`),
  CONSTRAINT `choices_places_ibfk_1` FOREIGN KEY (`choice_id`) REFERENCES `choices` (`choice_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
