#!/usr/bin/env python
# Public domain code (widely used)


def static_init(cls, init_f="static_init"):
    f = getattr(cls, init_f, None)
    assert f
    f()
    return cls
