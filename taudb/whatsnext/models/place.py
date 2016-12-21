class Place:

    def __init__(self, id, google_id, name, latitude, longitude, rating=None, vicinity=None):
        self.id = id
        self.google_id = google_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.rating = rating
        self.vicinity = vicinity

    def __repr__(self):
        return 'id:{id}, google_id:{google_id}, name:{name}'.format(id=self.id,
                                                                    google_id=self.google_id,
                                                                    name=self.name)
