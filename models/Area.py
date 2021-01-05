from base64 import b64decode
from tempfile import TemporaryFile

from mongoengine import Document, StringField, IntField, PointField, FileField, ReferenceField, ImageField, GridFSError

from utils.DualMap import DualMap

area_categories_map = DualMap({
    0: 'Room',
    1: 'Apartment',
    2: 'House',
    3: 'Office',
}, (-1, 'unknown'))


class Area(Document):
    owner = ReferenceField('User', required=True)
    name = StringField(required=True)
    category = IntField(required=True,
                        min_value=area_categories_map.minimum_key(),
                        max_value=area_categories_map.maximum_key())
    location = StringField(required=True)
    location_point = PointField()
    image = ImageField(size=(1920, 1080, False), thumbnail_size=(256, 256, False))

    def put_image(self, b64_image: str):
        file_like = b64decode(b64_image)
        bytes_image = bytearray(file_like)

        with TemporaryFile() as f:
            f.write(bytes_image)
            f.flush()
            f.seek(0)
            try:
                self.image.put(f)
            except GridFSError:
                self.image.replace(f)

    def to_dict(self):
        #
        # HACK: location point is list when the object was created, but gets saved
        # as a dict with a coordinates key containing the list
        #
        if isinstance(self.location_point, list):
            location_points = self.location_point
        elif isinstance(self.location_point, dict):
            location_points = self.location_point['coordinates']
        else:
            location_points = []

        return {
            'id': str(self.id),
            'owner': self.owner.to_dict(),
            'name': self.name,
            'category': self.category,
            'has_image': False,
            'no_devices': 0,
            'no_controllers': 0,
            'location': self.location,
            'location_point': location_points,
        }
