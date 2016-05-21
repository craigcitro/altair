import pandas as pd

try:
    import traitlets as T
except ImportError:
    from IPython.utils import traitlets as T


_attr_template = "Attribute not found: {0}. Valid keyword arguments for this class: {1}"

class BaseObject(T.HasTraits):

    skip = []

    def __init__(self, **kwargs):
        all_traits = list(self.traits())
        for k in kwargs:
            if k not in all_traits:
                raise KeyError(_attr_template.format(k, all_traits))
        super(BaseObject, self).__init__(**kwargs)

    def __contains__(self, key):
        try:
            value = getattr(self, key)
        except AttributeError:
            return False

        # comparison to None will break, so check DataFrame specifically
        if isinstance(value, pd.DataFrame):
            return True
        elif value is not None:
            if isinstance(value, (int, float, bool)):
                return True
            else:
                return bool(value)
        else:
            return False

    def __dir__(self):
        """Customize tab completed attributes."""
        return list(self.traits())+['to_dict']

    def to_dict(self):
        result = {}
        for k in self.traits():
            if k in self and k not in self.skip:
                v = getattr(self, k)
                if v is not None:
                    result[k] = trait_to_dict(v)
        return result

    @classmethod
    def from_json(cls, jsn):
        """Initialize object from a suitable JSON string"""
        return cls.from_dict(json.loads(jsn))

    @classmethod
    def from_dict(cls, dct):
        """Initialize a Layer from a vegalite JSON dictionary"""
        try:
            obj = cls()
        except TypeError as err:
            # TypeError indicates that an argument is missing
            obj = cls('')

        for prop, val in dct.items():
            if not obj.has_trait(prop):
                raise ValueError("{0} not a valid property in {1}"
                                 "".format(prop, klass))
            else:
                trait = obj.traits()[prop]
                if isinstance(trait, T.Instance):
                    obj.set_trait(prop, trait.klass.from_dict(val))
                else:
                    obj.set_trait(prop, val)
        return obj

    def update_traits(self, **kwargs):
        for key, val in kwargs.items():
            self.set_trait(key, val)
        return self


def trait_to_dict(obj):
    """Recursively convert object to dictionary"""
    if isinstance(obj, BaseObject):
        return obj.to_dict()
    elif isinstance(obj, list):
        return [trait_to_dict(o) for o in obj]
    else:
        return obj
