def test_assert_false():
    assert False, 'The assert should fail'  # xfail


def test_assert_passed():
    assert True, 'The assert should pass'
