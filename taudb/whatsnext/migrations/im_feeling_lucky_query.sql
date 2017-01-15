#q3: returns best rated bar, restaurant and hotels
# where the hotel is around a given spot,
#the restaurant is around the hotel
#and the bar is around the restaurant.
#bassicaly, it simulates a three steps search process 
SELECT hotel_id, restaurant_id, p.id AS bar_id
FROM(

	#returns best rated hotel and restaurant id's,
	#restaurany latitude and longitude AND best bar rate
	SELECT best_restaurant.*,MAX(p.rating) as max_rate_of_bar
	FROM(

		# q2: returns best rated hotel and restaurant id's 
		# and restaurany latitude and longitude
		SELECT best_hotel_and_restaurant_rate.hotel_id, p.id AS restaurant_id,
				p.latitude,p.longitude
		FROM(

			#get best rate restaurant and the hotel from q1
			SELECT best_hotel.*,MAX(p.rating) as max_rate_of_restaurant
			FROM(
			
				#q1: get best rate hotel in range
				SELECT p.id AS hotel_id, p.name AS hotel_name,
						p.latitude,p.longitude
				FROM places AS p 
				INNER JOIN
				places_categories AS pc ON p.id = pc.place_id
				WHERE p.latitude BETWEEN 5236 AND 5436 
					  AND p.longitude BETWEEN -25 AND 175
					  AND pc.category_id = 1
				ORDER BY rating DESC LIMIT 1
				
				) as best_hotel,
			places AS p INNER JOIN
			places_categories AS pc ON p.id = pc.place_id
			WHERE p.latitude BETWEEN best_hotel.latitude - 0.5*10000/111.0 
			AND best_hotel.latitude + 0.5*10000/111.0 
			AND  p.longitude BETWEEN best_hotel.longitude - 0.5*10000/69.0 
			AND best_hotel.longitude + 0.5*10000/69.0
			AND pc.category_id = 2
				
				) AS best_hotel_and_restaurant_rate,
		places AS p INNER JOIN
		places_categories AS pc ON p.id = pc.place_id
		WHERE p.latitude BETWEEN best_hotel_and_restaurant_rate.latitude - 0.5*10000/111.0 
		AND best_hotel_and_restaurant_rate.latitude + 0.5*10000/111.0 
		AND  p.longitude BETWEEN best_hotel_and_restaurant_rate.longitude - 0.5*10000/69.0 
		AND best_hotel_and_restaurant_rate.longitude + 0.5*10000/69.0
		AND pc.category_id = 2 
		AND p.rating = best_hotel_and_restaurant_rate.max_rate_of_restaurant
				)AS best_restaurant,
	places AS p INNER JOIN
	places_categories AS pc ON p.id = pc.place_id
	WHERE p.latitude BETWEEN best_restaurant.latitude - 0.5*10000/111.0 
	AND best_restaurant.latitude + 0.5*10000/111.0 
	AND  p.longitude BETWEEN best_restaurant.longitude - 0.5*10000/69.0 
	AND best_restaurant.longitude + 0.5*10000/69.0
	AND pc.category_id = 3
                ) AS best_restaurant_and_bar_rate,
places AS p INNER JOIN
places_categories AS pc ON p.id = pc.place_id
WHERE p.latitude BETWEEN best_restaurant_and_bar_rate.latitude - 0.5*10000/111.0 
AND best_restaurant_and_bar_rate.latitude + 0.5*10000/111.0 
AND  p.longitude BETWEEN best_restaurant_and_bar_rate.longitude - 0.5*10000/69.0 
AND best_restaurant_and_bar_rate.longitude + 0.5*10000/69.0
AND pc.category_id = 3 
AND p.rating = best_restaurant_and_bar_rate.max_rate_of_bar
LIMIT 1
                
    
    
     
    
    
    
    