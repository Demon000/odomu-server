from mongoengine import Document, StringField, BinaryField
import bcrypt


def encode_string(password):
    if type(password) == str:
        password = password.encode('utf-8')

    return password


class User(Document):
    username = StringField(required=True, unique=True)
    password = BinaryField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)

    def set_password(self, password):
        password = encode_string(password)
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def is_correct_password(self, password):
        password = encode_string(password)
        return bcrypt.checkpw(password, self.password)

    def to_dict(self):
        return {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }
