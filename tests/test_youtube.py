from sources.youtube import parse_duration

def test_duration():
    assert parse_duration('PT5M')==300
    assert parse_duration('PT1H2M3S')==3723
