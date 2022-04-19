import re
import datetime

from .access_level import AccessLevel


class User:
    BIRTHDAY_FORMAT = r'%Y-%m-%d'
    PHONE_FORMAT = r'\+(\d{2})(\d{2})([1-9]\d{7,8})'
    SOCIAL_NUMBER = r'\d{3}.\d{3}.\d{3}-\d{2}|\d{11}'
 
    def __init__(self, name, birthday, social_number, phone, access_level):
        self.name = name
        self.birthday = datetime.datetime.strptime(birthday, User.BIRTHDAY_FORMAT)
        if not re.match(User.SOCIAL_NUMBER, social_number):
            raise ValueError('invalid social number')
        self.social_number = social_number
        if not re.match(User.PHONE_FORMAT, phone):
            raise ValueError('invalid phone number')
        self.phone = phone
        if not isinstance(access_level, AccessLevel):
            raise ValueError('access type must be a AccessLevel object')
        self.access_level = access_level
    
    def __eq__(self, o: object):
        return isinstance(o, User) and self.to_dict() == o.to_dict()

    @property
    def age(self):
        return (datetime.datetime.today() - self.birthday).days // 365

    def to_dict(self):
        return {'name': self.name,
                'birthday': self.birthday.strftime(User.BIRTHDAY_FORMAT),
                'social_number': self.social_number,
                'phone': self.phone,
                'access_level': self.access_level}

    @staticmethod
    def from_dict(self, props):
        pass
