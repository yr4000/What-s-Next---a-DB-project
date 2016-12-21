CREATE TABLE places (
  `id` int NOT NULL AUTO_INCREMENT,
  `google_id` varchar(50) UNIQUE NOT NULL,
  `name` varchar(255) NOT NULL,
  `rating` float default NULL,
  `price_level` tinyint default NULL,
  `vicinity` varchar(255) default NULL,
  `latitude` float(10,10) NOT NULL,
  `longitude` float(10,10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_google_id` (`google_id`),
  KEY `idx_name` (`name`),
  KEY `idx_rating` (`rating`),
  KEY `idx_price_level` (`price_level`),
  KEY `idx_address` (`vicinity`),
  KEY `idx_latitude` (`latitude`),
  KEY `idx_longitude` (`longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;