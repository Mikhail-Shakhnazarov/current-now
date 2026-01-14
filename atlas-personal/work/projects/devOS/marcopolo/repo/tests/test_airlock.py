from marcopolo.util import airlock_text

def test_airlock_ascii_ok():
    s, rep = airlock_text("hello", repair_common_punct=False)
    assert s == "hello"
    assert rep["ascii_ok"] is True

def test_airlock_repair_punct():
    s, rep = airlock_text("hi\u2014there", repair_common_punct=True)
    assert s == "hi--there"
    assert rep["ascii_ok"] is True
    assert rep["repaired"] is True
