from typing import Union

from models.Area import area_categories_map
from models.User import User
from utils.errors import AreaCategoryInvalid, AreaNameInvalid, AreaLocationInvalid, AreaOwnerInvalid
from validators.Validator import Validator


class AreaValidator(Validator):
    def parse_category(self, value: Union[str, int]):
        if value is None:
            raise AreaCategoryInvalid('Cannot be empty')

        try:
            value = int(value)
        except ValueError:
            pass

        value = area_categories_map.to_key_either(value)
        if value < 0:
            raise AreaCategoryInvalid("Must be one of")

        return value

    def validate_owner(self, value: User):
        if type(value) != User:
            raise AreaOwnerInvalid()

    def validate_name(self, value: str):
        self.validate_str('Area name', AreaNameInvalid, value)

    def validate_location(self, value: str):
        self.validate_str('Area location', AreaLocationInvalid, value)
