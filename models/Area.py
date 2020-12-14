from mongoengine import Document, StringField, IntField, PointField, FileField, ReferenceField

from utils.DualMap import DualMap

area_categories = DualMap({
    1: 'Room',
    2: 'Apartment',
    3: 'House',
    4: 'Office',
})


class Area(Document):
    owner = ReferenceField('User', required=True)
    name = StringField(required=True)
    category = IntField(required=True,
                        min_value=area_categories.minimum_key(),
                        max_value=area_categories.maximum_key())
    location = StringField(required=True)
    location_point = PointField()
    image = FileField()

    def to_dict(self, with_details=False):
        d = {
            'owner': self.owner,
            'name': self.name,
            'category': self.category,
            'category_text': area_categories.to_value(self.category),
            'has_image': False,
        }

        if with_details:
            d['no_devices'] = 0
            d['no_controllers'] = 0
            d['location'] = self.location
            d['location_point'] = self.location_point

        return d
