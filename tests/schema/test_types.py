import pytest

from align.schema.types import BaseModel, List, Dict, SpiceStr


class BaseType(BaseModel):
    name: SpiceStr


class CompositionalType(BaseModel):
    name: SpiceStr
    child: BaseType
    children: List[BaseType]
    children_as_dict: Dict[SpiceStr, BaseType]


def test_type_inference():
    myobj = CompositionalType(**{
        'name': 'toplevel',
        'child': {'name': 'orphanchild'},
        'children': [
            {'name': 'child1'},
            {'name': 'child2'}
        ],
        'children_as_dict': {
            'child1': {'name': 'child1'},
            'child2': {'name': 'child2'},
        }
    })
    assert isinstance(myobj, CompositionalType)
    assert isinstance(myobj.child, BaseType)
    assert isinstance(myobj.children, List)
    assert isinstance(myobj.children_as_dict, Dict)
    assert all(isinstance(x, BaseType) for x in myobj.children)
    assert all(isinstance(x, SpiceStr) for x in myobj.children_as_dict.keys())
    assert all(isinstance(x, BaseType) for x in myobj.children_as_dict.values())

def test_type_relationships():
    myobj = CompositionalType(
        name='toplevel',
        child={'name': 'orphanchild'},
        children=[
            {'name': 'child1'},
            {'name': 'child2'}
        ],
        children_as_dict={
            'child1': {'name': 'child1'},
            'child2': {'name': 'child2'},
        }
    )
    assert myobj.parent is None, id(myobj.parent)
    assert myobj.child.parent == myobj
    assert len(myobj.children) == 2
    child1, child2 = myobj.children
    assert child1.parent == child2.parent
    assert child1.parent.parent == myobj
    assert len(myobj.children_as_dict) == 2
    assert myobj.children_as_dict['child1'].parent == myobj.children_as_dict['child2'].parent
    assert myobj.children_as_dict['child1'].parent.parent == myobj

def test_case_insensitive_string():
    # Core functionality we are trying to achieve
    assert SpiceStr("Steve") == SpiceStr("steve")
    assert SpiceStr("Steve") != SpiceStr("burns")

    # Comparison to built-in str works 
    # both ways as well !!!
    assert "sTeVe" == SpiceStr("Steve")
    assert SpiceStr("Steve") == "sTeVe"
    assert "burns" != SpiceStr("Steve")
    assert SpiceStr("Steve") != "burns"

    # As long as parent string is of type
    # `SpiceStr`, contains works as expected
    assert SpiceStr("Ste") in SpiceStr("steve")
    assert "sTeVe" in SpiceStr("steve")
    assert "StE" in SpiceStr("steve")
    assert "Burns" not in SpiceStr("steve")
    # WARNING: parent string MUST be of type
    # `SpiceStr` for contain to work. See below
    assert SpiceStr("ste") not in "Steve"

    # WARNING: Object behaves like built-in str
    # for almost everything else

    # Slicing returns built-in str (not `SpiceStr`)
    x, y = SpiceStr("Steve")[0], SpiceStr("Steve")[0:3]
    assert type(x) == str
    assert type(y) == str
    assert x == 'S'
    assert y == 'Ste'
    # Reverse via slicing works returns
    # built-in str (not `SpiceStr`)
    x = SpiceStr("Steve")[::-1]
    assert type(x) == str
    assert x == "evetS"

    # `reverse` returns iterator
    assert list(reversed(SpiceStr("Steve"))) == list("evetS")

    # len, list comprehension etc works like str
    assert len(SpiceStr("Steve")) == 5
    assert list("Steve") == [c for c in SpiceStr("Steve")]
