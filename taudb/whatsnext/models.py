# from __future__ import unicode_literals
import datetime


class Serializable(object):  # TODO: move this class elsewhere
    def to_json(self):
        return self.__dict__


class Place(Serializable):

    def __init__(self, place_id, google_id, name, latitude, longitude, category, rating=None, vicinity=None):
        self.place_id = place_id
        self.google_id = google_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.category = category
        self.rating = rating
        self.vicinity = vicinity

    def __repr__(self):
        return '<id:{id}, google_id:{google_id}, name:{name}>'.format(id=self.place_id,
                                                                      google_id=self.google_id,
                                                                      name=self.name)


class Review(Serializable):

    def __init__(self, review_id, place_id, author, rating, text, date):
        self.review_id = review_id
        self.place_id = place_id
        self.author = author
        self.rating = rating
        self.text = text
        if type(date) == str:
            datetime.date.strftime(date, '%Y-%m-%d')
            self.date = date
        else:
            self.date = date

    def __repr__(self):
        return '<id:{id}, place_id: {place_id}, author:{author}>'.format(id=self.review_id,
                                                                         place_id=self.place_id,
                                                                         author=self.author)


class Category(Serializable):

    def __init__(self, category_id, name):
        self.category_id = category_id
        self.name = name

    def __repr__(self):
        return '<id:{id}, name:{name}>'.format(id=self.category_id, name=self.name)



