import pydantic

from typing import Union, Dict, ClassVar, Optional

from .model import Model
from .subcircuit import SubCircuit

class Instance(pydantic.BaseModel):

    model: Union[Model, SubCircuit]
    name: str
    pins : Dict[str, str]
    parameters : Optional[Dict[str, str]]

    def json(self):
        return super().json(include=self.jsonfilter)

    def xyce(self):
        return f'{self.name} ' + \
            ' '.join(self.pins.values()) + \
            f' {self.model.name} ' + \
            ' '.join(f'{x}={{{y}}}' for x, y in self.parameters.items())

    #
    # Private attributes affecting class behavior
    #

    class Config:
        validate_assignment = True
        extra = 'forbid'
        allow_mutation = False

    jsonfilter: ClassVar[Dict] = {
        'model': {'name'},
        'name': ...,
        'pins' : ...,
        'parameters' : ...
    }

    @pydantic.validator('name')
    def name_complies_with_model(cls, name, values):
        name = name.upper()
        assert 'model' in values, 'Cannot run check without model definition'
        if values['model'].prefix and not name.startswith(values['model'].prefix):
            logger.error(f"{name} does not start with {values['model'].prefix}")
            raise AssertionError(f"{name} does not start with {values['model'].prefix}")
        return name

    @pydantic.validator('pins')
    def pins_comply_with_model(cls, pins, values):
        pins = {k.upper(): v.upper() for k, v in pins.items()}
        assert 'model' in values, 'Cannot run check without model definition'
        assert set(pins.keys()) == set(values['model'].pins)
        return pins

    @pydantic.validator('parameters', always=True)
    def parameters_comply_with_model(cls, parameters, values):
        assert 'model' in values, 'Cannot run check without model definition'
        if parameters:
            parameters = {k.upper(): v.upper() for k, v in parameters.items()}
            assert values['model'].parameters and set(parameters.keys()).issubset(values['model'].parameters.keys()), \
                f"{self.__class__.__name__} parameters must be a subset of {values['model'].__class__.__name__} parameters"
            parameters = {k: parameters[k] if k in parameters else v \
                for k, v in values['model'].parameters.items()}
        elif values['model'].parameters:
            parameters = values['model'].parameters.copy()
        return parameters
