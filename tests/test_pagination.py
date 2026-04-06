from app.api.routes import paginate


def test_paginate_default():
    items = list(range(10))
    page, total = paginate(items, 1, 3)
    assert page == [3, 4, 5]
    assert total == 10


def test_paginate_disabled():
    items = list(range(4))
    page, total = paginate(items, 0, 0)
    assert page == [0, 1, 2, 3]
    assert total == 4
