import os
from catatom3dfix import CatChangeset, OsmChangeset


def setup_module(module):
    os.chdir('test')

def test_void_result():
    """
    Buildings without associated parts and buildings fully covered with parts 
    should be ignored and no output file generated.
    """
    cs = CatChangeset('1.osm')
    cs.get_missing_parts()
    assert len(cs.osc.ways) + len(cs.osc.relations) == 0

def test_single_part():
    """
    Result is a single part
    """
    cs = CatChangeset('2.osm')
    cs.get_missing_parts()
    assert len(cs.osc.ways) == 1
    assert len(cs.osc.relations) == 0
    w = cs.osc.ways[0]
    assert w.nodes == [
        5994936452, 5994936414, 5994936448, 5994936449, 5994936450, 5994936452
    ]
    assert w.tags == {
        'building:levels': '2',
        'building:levels:underground': '1',
        'building:part': 'yes'
    }
    assert w.id < 0

def test_multi_part():
    """
    Result have multiple parts
    """
    cs = CatChangeset('3.osm')
    cs.get_missing_parts()
    assert len(cs.osc.ways) == 2
    assert len(cs.osc.relations) == 0
    w1 = cs.osc.ways[0]
    w2 = cs.osc.ways[1]
    assert w1.nodes == [
        5994936539, 5994936511, 5994936547, 5994936457, 5994936556, 5994936539
    ]
    assert w1.tags == {'building:levels': '2', 'building:part': 'yes'}
    assert w1.id < 0
    assert w2.nodes == [
        5994936553, 5994936395, 5994936479, 5994936539, 5994936560, 5994936553
    ]
    assert w2.tags == {'building:levels': '2', 'building:part': 'yes'}
    assert w2.id < 0

def test_mp_input():
    """
    Input have multipolygon relations
    """
    cs = CatChangeset('4.osm')
    cs.get_missing_parts()
    assert len(cs.osc.ways) == 1
    assert len(cs.osc.relations) == 0
    w = cs.osc.ways[0]
    assert w.nodes == [
        5994936548, 5994936550, 5994936551, 5994936471, 5994936519, 5994936548
    ]
    assert w.tags == {
        'building:levels': '4',
        'building:levels:underground': '1',
        'building:part': 'yes'
    }
    assert w.id < 0

def test_mp_output():
    """
    Output have multipolygon relations
    """
    cs = CatChangeset('5.osm')
    cs.get_missing_parts()
    assert len(cs.osc.ways) == 2
    assert len(cs.osc.relations) == 1
    w1 = cs.osc.ways[0]
    w2 = cs.osc.ways[1]
    r = cs.osc.relations[0]
    assert w1.id == 635546291
    assert w2.id == 635546283
    assert r.members == [
        ('way', 635546291, 'outer'), ('way', 635546283, 'inner')
    ]
    assert r.tags == {
        'building:levels': '2', 'building:part': 'yes', 'type': 'multipolygon'
    }
    assert r.id < 0

