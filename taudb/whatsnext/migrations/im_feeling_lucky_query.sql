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