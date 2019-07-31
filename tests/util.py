from copy import deepcopy
from contextlib import contextmanager


@contextmanager
def backup_attributes(obj, attributes):
    """
    Makes a backup of the object attributes that gets restored later.
    """
    obj_dict = obj.__dict__
    # creates a subset dictionary of the attributes we're interested in
    attributes_backup = dict(
        (k, obj_dict[k]) for k in attributes if k in obj_dict)
    attributes_backup = deepcopy(attributes_backup)
    try:
        yield
    finally:
        for attribute in attributes:
            setattr(obj, attribute, attributes_backup[attribute])
