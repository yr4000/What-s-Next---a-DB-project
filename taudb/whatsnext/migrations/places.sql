CREATE TABLE places (
    `id` INT NOT NULL AUTO_INCREMENT,
    `google_id` VARCHAR(50) UNIQUE NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `rating` FLOAT DEFAULT NULL,
    `vicinity` VARCHAR(255) DEFAULT NULL,
    `latitude` FLOAT(10 , 7 ) NOT NULL,
    `longitude` FLOAT(10 , 7 ) NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_google_id` (`google_id`),
    KEY `idx_name` (`name`),
    KEY `idx_rating` (`rating`),
    KEY `idx_address` (`vicinity`),
    KEY `idx_latitude` (`latitude`),
    KEY `idx_longitude` (`longitude`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;


CREATE TABLE categories (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;

INSERT INTO categories (`name`) VALUES ('lodging');
INSERT INTO categories (`name`) VALUES ('restaurant');


CREATE TABLE places_categories (
    `id` INT NOT NULL AUTO_INCREMENT,
    `place_id` INT NOT NULL,
    `category_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fgn_place_id` FOREIGN KEY (`place_id`) REFERENCES places (`id`),
    CONSTRAINT `fgn_category_id` FOREIGN KEY (`category_id`) REFERENCES categories (`id`),
	UNIQUE KEY `place_id_category_id` (`place_id`,`category_id`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;


SELECT 
    places.id, places.google_id, categories.id, categories.name
FROM
    places
        INNER JOIN
    places_categories ON places.id = places_categories.place_id
        INNER JOIN
    categories ON places_categories.category_id = categories.id
WHERE
    places_categories.category_id=2;

        