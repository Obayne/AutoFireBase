from __future__ import annotations


def align_left(items):
    _align(items, key=lambda it: it.rect().left(), setter=lambda it, x: _move_x(it, x))


def align_right(items):
    _align(
        items,
        key=lambda it: it.rect().right(),
        setter=lambda it, x: _move_x(it, x - it.rect().width()),
    )


def align_top(items):
    _align(items, key=lambda it: it.rect().top(), setter=lambda it, y: _move_y(it, y))


def align_bottom(items):
    _align(
        items,
        key=lambda it: it.rect().bottom(),
        setter=lambda it, y: _move_y(it, y - it.rect().height()),
    )


def distribute_h(items):
    if len(items) < 3:
        return
    items = sorted(items, key=lambda it: it.rect().left())
    left = items[0].rect().left()
    right = items[-1].rect().left()
    step = (right - left) / (len(items) - 1)
    for i, it in enumerate(items):
        _move_x(it, left + i * step)


def distribute_v(items):
    if len(items) < 3:
        return
    items = sorted(items, key=lambda it: it.rect().top())
    top = items[0].rect().top()
    bottom = items[-1].rect().top()
    step = (bottom - top) / (len(items) - 1)
    for i, it in enumerate(items):
        _move_y(it, top + i * step)


def _align(items, key, setter):
    if not items:
        return
    target = min(items, key=key)
    val = key(target)
    for it in items:
        setter(it, val)


def _move_x(it, x):
    r = it.rect()
    it.setPos(x, r.top())


def _move_y(it, y):
    r = it.rect()
    it.setPos(r.left(), y)
