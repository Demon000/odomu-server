from mongoengine import Document, StringField, IntField, PointField, FileField, ReferenceField

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
    image = FileField()

    def to_dict(self):
        return {
            'id': str(self.id),
            'owner': self.owner.to_dict(),
            'name': self.name,
            'category': self.category,
            'category_text': area_categories_map.to_value(self.category),
            'has_image': False,
            'no_devices': 0,
            'no_controllers': 0,
            'location': self.location,
            'location_point': self.location_point,
        }
