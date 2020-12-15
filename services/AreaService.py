from typing import Union

from models.Area import Area
from models.User import User
from utils.errors import AreaCategoryInvalid, AreaAddFailed, AreaNameInvalid, AreaLocationInvalid,\
    AreaUpdateFailed, AreaOwnerInvalid
from validators.AreaValidator import AreaValidator


class AreaService:
    def __init__(self, validator: AreaValidator):
        self.__validator = validator

    def add(self, owner: User, name: str, category: Union[str, int], location: str):
        me = AreaAddFailed()

        try:
            self.__validator.validate_owner(owner)
        except AreaOwnerInvalid as e:
            me.add_error(e)

        try:
            self.__validator.validate_name(name)
        except AreaNameInvalid as e:
            me.add_error(e)

        try:
            category = self.__validator.parse_category(category)
        except AreaCategoryInvalid as e:
            me.add_error(e)

        try:
            self.__validator.validate_location(name)
        except AreaLocationInvalid as e:
            me.add_error(e)

        if not me.is_empty():
            raise me

        area = Area(owner=owner, name=name, category=category, location=location)

        area.save()

        return area

    def find_one_by(self, *args, **kwargs):
        return Area.objects.get(*args, **kwargs)

    def find_by(self, *args, **kwargs):
        return Area.objects(*args, **kwargs)

    def update(self, area: Area, name: str, category: Union[str, int], location: str):
        me = AreaUpdateFailed()

        if name is not None:
            try:
                self.__validator.validate_name(name)
                area.name = name
            except AreaNameInvalid as e:
                me.add_error(e)

        if category is not None:
            try:
                category = self.__validator.parse_category(category)
                area.category = category
            except AreaCategoryInvalid as e:
                me.add_error(e)

        if location is not None:
            try:
                self.__validator.validate_location(name)
                area.location = location
            except AreaLocationInvalid as e:
                me.add_error(e)

        if not me.is_empty():
            raise me

        area.save()

    def delete(self, area: Area):
        area.delete()
