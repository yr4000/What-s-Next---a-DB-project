-- this is version 1 - BFS of a single tree branch:
SELECT hotel_id, hotel_name, hotel_lat, hotel_long,
            rest_id,rest_name,rest_lat,rest_long,                                                     
            p.id AS bar_id, p.name AS bar_name,p.latitude As bar_lat, p.longitude AS long_lat         
            FROM(                                                                                     
            	SELECT best_restaurant.*,MAX(p.rating) as max_rate_of_bar                              
            	FROM(                                                                                  
            		SELECT hotel_id, hotel_name, hotel_lat,hotel_long, p.id AS rest_id,                
            				p.name AS rest_name, p.latitude AS rest_lat, p.longitude AS rest_long      
            		FROM(                                                                              
                                                                                                      
            			#get best rate restaurant and the hotel from q1                                
            			SELECT best_hotel.*,MAX(p.rating) as max_rate_of_restaurant                    
            			FROM(                                                                          
            			                                                                               
            				#q1: get best rate hotel in range                                          
            				SELECT p.id AS hotel_id, p.name AS hotel_name,                             
                                  p.latitude AS hotel_lat ,p.longitude AS hotel_long                  
            				FROM places AS p                                                           
            				INNER JOIN                                                                 
            				places_categories AS pc ON p.id = pc.place_id                              
            				WHERE p.latitude BETWEEN 4735 AND 5636                                         
            					  AND p.longitude BETWEEN -1837 AND -387                                    
            					  AND pc.category_id = 1                                               
            				ORDER BY rating DESC LIMIT 1                                               
            				                                                                           
            				) as best_hotel,                                                           
            			places AS p INNER JOIN                                                         
            			places_categories AS pc ON p.id = pc.place_id                                  
            			WHERE p.latitude BETWEEN hotel_lat - 0.5*10000/111.0                    
            			AND hotel_lat + 0.5*10000/111.0                                         
            			AND  p.longitude BETWEEN hotel_long - 0.5*10000/69.0                  
            			AND hotel_long + 0.5*10000/69.0                                       
                       AND p.id != hotel_id                                                           
            			AND pc.category_id = 2                                                         
            				                                                                           
            				) AS best_hotel_and_restaurant_rate,                                       
            		places AS p INNER JOIN                                                             
            		places_categories AS pc ON p.id = pc.place_id                                      
            		WHERE p.latitude BETWEEN hotel_lat - 0.5*10000/111.0                        
            		AND hotel_lat + 0.5*10000/111.0                                             
            		AND  p.longitude BETWEEN hotel_long - 0.5*10000/69.0                      
            		AND hotel_long + 0.5*10000/69.0                                           
            		AND pc.category_id = 2                                                             
                   AND p.id != hotel_id                                                               
            		AND p.rating = max_rate_of_restaurant                                              
                   LIMIT 1                                                                            
            				)AS best_restaurant,                                                       
            	places AS p INNER JOIN                                                                 
            	places_categories AS pc ON p.id = pc.place_id                                          
            	WHERE p.latitude BETWEEN rest_lat - 0.5*10000/111.0                             
            	AND rest_lat + 0.5*10000/111.0                                                  
            	AND  p.longitude BETWEEN rest_long - 0.5*10000/69.0                           
            	AND rest_long + 0.5*10000/69.0                                                
               AND p.id != rest_id                                                                    
            	AND pc.category_id = 3                                                                 
                            ) AS best_restaurant_and_bar_rate,                                        
            places AS p INNER JOIN                                                                    
            places_categories AS pc ON p.id = pc.place_id                                             
            WHERE p.latitude BETWEEN rest_lat - 0.5*10000/111.0                                
            AND rest_lat + 0.5*10000/111.0                                                     
            AND  p.longitude BETWEEN rest_long - 0.5*10000/69.0                              
            AND rest_long + 0.5*10000/69.0                                                   
            AND p.id != rest_id                                                                       
            AND pc.category_id = 3                                                                    
            AND p.rating = max_rate_of_bar                                                            
            LIMIT 1






SELECT
    p.id AS bar_id,
    p.name AS bar_name,
    p.rating AS bar_rating,
    p.vicinity AS bar_vicinity,
    p.latitude AS bar_latitude,
    p.longitude AS bar_longitude,
    c.name AS bar_category,
    best_hotels_restaurants.*,
    p.rating + best_hotels_restaurants.restaurant_rating + best_hotels_restaurants.hotel_rating AS total_rating
FROM
    (places AS p
    INNER JOIN places_categories AS pc ON p.id = pc.place_id
    INNER JOIN categories AS c ON c.id = pc.category_id),
    (SELECT
        p.id AS restaurant_id,
            p.name AS restaurant_name,
            p.rating AS restaurant_rating,
            p.vicinity AS restaurant_vicinity,
            p.latitude AS restaurant_latitude,
            p.longitude AS restaurant_longitude,
            c.name AS restaurant_category,
            best_hotels.*
    FROM
        (places AS p
    INNER JOIN places_categories AS pc ON p.id = pc.place_id
    INNER JOIN categories AS c ON c.id = pc.category_id), (SELECT
        p.id AS hotel_id,
            p.name AS hotel_name,
            p.rating AS hotel_rating,
            p.vicinity AS hotel_vicinity,
            p.latitude AS hotel_latitude,
            p.longitude AS hotel_longitude,
            c.name AS hotel_category
    FROM
        places AS p
    INNER JOIN places_categories AS pc ON p.id = pc.place_id
    INNER JOIN categories AS c ON c.id = pc.category_id
    WHERE
        c.name = 'hotel'
            AND p.latitude BETWEEN 4735 AND 5636
            AND p.longitude BETWEEN - 1837 AND - 387
            AND p.rating = (SELECT
                MAX(p.rating)
            FROM
                places AS p
            INNER JOIN places_categories AS pc ON p.id = pc.place_id
            INNER JOIN categories AS c ON c.id = pc.category_id
            WHERE
                c.name = 'hotel'
                    AND p.latitude BETWEEN 4735 AND 5636
                    AND p.longitude BETWEEN - 1837 AND - 387)) AS best_hotels
    WHERE
        c.name = 'restaurant'
            AND p.latitude BETWEEN hotel_latitude - (0.5 * 10000 / 111.0) AND hotel_latitude + (0.5 * 10000 / 111.0)
            AND p.longitude BETWEEN hotel_longitude - (0.5 * 10000 / 69.0) AND hotel_longitude + (0.5 * 10000 / 69.0)
            AND p.rating = (SELECT
                MAX(p.rating)
            FROM
                places AS p
            INNER JOIN places_categories AS pc ON p.id = pc.place_id
            INNER JOIN categories AS c ON c.id = pc.category_id
            WHERE
                c.name = 'restaurant'
                    AND p.latitude BETWEEN hotel_latitude - (0.5 * 10000 / 111.0) AND hotel_latitude + (0.5 * 10000 / 111.0)
                    AND p.longitude BETWEEN hotel_longitude - (0.5 * 10000 / 69.0) AND hotel_longitude + (0.5 * 10000 / 69.0))) best_hotels_restaurants
WHERE
    c.name = 'bar'
        AND p.latitude BETWEEN restaurant_latitude - (0.5 * 10000 / 111.0) AND restaurant_latitude + (0.5 * 10000 / 111.0)
        AND p.longitude BETWEEN restaurant_longitude - (0.5 * 10000 / 69.0) AND restaurant_longitude + (0.5 * 10000 / 69.0)
        AND p.rating = (SELECT
            MAX(p.rating)
        FROM
            places AS p
                INNER JOIN
            places_categories AS pc ON p.id = pc.place_id
                INNER JOIN
            categories AS c ON c.id = pc.category_id
        WHERE
            c.name = 'bar'
                AND p.latitude BETWEEN restaurant_latitude - (0.5 * 10000 / 111.0) AND restaurant_latitude + (0.5 * 10000 / 111.0)
                AND p.longitude BETWEEN restaurant_longitude - (0.5 * 10000 / 69.0) AND restaurant_longitude + (0.5 * 10000 / 69.0))
ORDER BY total_rating DESC;
