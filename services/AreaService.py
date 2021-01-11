from enum import Enum
from typing import Union, List

from pyee import BaseEventEmitter

from models.Area import Area
from models.User import User
from utils.errors import AreaCategoryInvalid, AreaAddFailed, AreaNameInvalid, AreaLocationInvalid, \
    AreaUpdateFailed, AreaOwnerInvalid, AreaLocationPointInvalid, AreaImageInvalid, AreaUpdatedAtTimestampInvalid
from validators.AreaValidator import AreaValidator


class AreaServiceEvents(Enum):
    AREA_ADDED = 'area-added'
    AREA_DELETED = 'area-deleted'
    AREA_UPDATED = 'area-updated'


class AreaService:
    def __init__(self, validator: AreaValidator):
        self.__validator = validator

        self.emitter = BaseEventEmitter()

    def add(self, owner: User, name: str, category: Union[str, int], location: str, location_point: List[float],
            image: str = None):
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
            self.__validator.validate_location(location)
        except AreaLocationInvalid as e:
            me.add_error(e)

        try:
            self.__validator.validate_location_point(location_point)
        except AreaLocationPointInvalid as e:
            me.add_error(e)

        area = Area(owner=owner, name=name, category=category, location=location, location_point=location_point)

        if image:
            try:
                area.put_b64_image(image)
            except Exception as e:
                ae = AreaImageInvalid(original_message=str(e))
                me.add_error(ae)

        if not me.is_empty():
            raise me

        area.save()

        self.emitter.emit(AreaServiceEvents.AREA_ADDED, area)

        return area

    def find_one_by(self, *args, **kwargs):
        return Area.objects.get(*args, **kwargs)

    def find_by(self, *args, **kwargs):
        return Area.objects(*args, **kwargs)

    def update(self, area: Area, name: str, category: Union[str, int], location: str, location_point: List[float],
               image: str, updated_at_timestamp: int):
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
                self.__validator.validate_location(location)
                area.location = location
            except AreaLocationInvalid as e:
                me.add_error(e)

        if location_point is not None:
            try:
                self.__validator.validate_location_point(location_point)
                area.location_point = location_point
            except AreaLocationPointInvalid as e:
                me.add_error(e)

        try:
            self.__validator.validate_updated_at_timestamp(area.updated_at_timestamp, updated_at_timestamp)
        except AreaUpdatedAtTimestampInvalid as e:
            me.add_error(e)

        if image:
            try:
                area.put_b64_image(image)
            except Exception as e:
                ae = AreaImageInvalid(original_message=str(e))
                me.add_error(ae)

        if not me.is_empty():
            raise me

        area.save()

        self.emitter.emit(AreaServiceEvents.AREA_UPDATED, area)

    def delete(self, area: Area):
        area.delete()

        self.emitter.emit(AreaServiceEvents.AREA_DELETED, area)
