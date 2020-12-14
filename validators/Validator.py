from typing import Type, List, Tuple, Callable

from utils.errors import ValidationError


class Validator:
    def validate_str(self, name: str, error_class: Type[ValidationError], value: str,
                     min_length: int = None, optional: bool = False):
        if optional is False and min_length is None:
            min_length = 1

        if value is None:
            if optional:
                return

            raise error_class("{} cannot be empty".format(name))

        if type(value) != str:
            raise error_class("{} must be a string".format(name))

        if min_length is not None and len(value) < min_length:
            raise error_class("{} must be at least {} characters long".format(name, min_length))
