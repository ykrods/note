from apps.myapp import compare

def test_compare():
    assert compare(1, 2) is -1
    assert compare(2, 1) is 1
