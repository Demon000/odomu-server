from base64 import b64decode, b64encode
from datetime import datetime
from tempfile import TemporaryFile

from mongoengine import Document, StringField, IntField, PointField, ReferenceField, ImageField, GridFSError, \
    GridFSProxy, DateTimeField

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
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def get_timestamp_common(self, field) -> int:
        return int(field.timestamp())

    @property
    def created_at_timestamp(self):
        return self.get_timestamp_common(self.created_at)

    @property
    def updated_at_timestamp(self):
        return self.get_timestamp_common(self.updated_at)

    def put_b64_image(self, b64_string: str):
        byte_string = b64decode(b64_string)
        byte_array = bytearray(byte_string)

        with TemporaryFile() as f:
            f.write(byte_array)
            f.flush()
            f.seek(0)
            try:
                self.image.put(f)
            except GridFSError:
                self.image.replace(f)

    def get_b64_image_common(self, image: GridFSProxy):
        byte_array = image.read()
        byte_string = bytes(byte_array)
        b64_string = b64encode(byte_string)
        return b64_string.decode('utf-8')

    def to_dict(self, with_image: bool = False, with_thumbnail: bool = False):
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

        d = {
            'id': str(self.id),
            'owner': self.owner.to_dict(),
            'name': self.name,
            'category': self.category,
            'has_image': bool(self.image),
            'no_devices': 0,
            'no_controllers': 0,
            'location': self.location,
            'location_point': location_points,
            'created_at_timestamp': self.created_at_timestamp,
            'updated_at_timestamp': self.updated_at_timestamp,
        }

        if with_image and self.image:
            d['image'] = self.get_b64_image_common(self.image)

        if with_thumbnail and self.image and self.image.thumbnail:
            d['thumbnail'] = self.get_b64_image_common(self.image.thumbnail)

        return d

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()

        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
