##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# flake8: noqa
import unittest


class Test_dispatchUtilityRegistrationEvent(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.registry import dispatchUtilityRegistrationEvent
        return dispatchUtilityRegistrationEvent(*args, **kw)

    def test_it(self):
        from guillotina.component import registry
        class _Registration(object):
            component = object()
        _EVENT = object()
        _handled = []
        def _handle(*args):
            _handled.append(args)
        with _Monkey(registry, handle=_handle):
            self._callFUT(_Registration(), _EVENT)
        self.assertEqual(_handled, [(_Registration.component, _EVENT)])


class Test_dispatchAdapterRegistrationEvent(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.registry import dispatchAdapterRegistrationEvent
        return dispatchAdapterRegistrationEvent(*args, **kw)

    def test_it(self):
        from guillotina.component import registry
        class _Registration(object):
            def factory(self, *args, **kw):
                pass
        _registration = _Registration()
        _EVENT = object()
        _handled = []
        def _handle(*args):
            _handled.append(args)
        with _Monkey(registry, handle=_handle):
            self._callFUT(_registration, _EVENT)
        self.assertEqual(_handled, [(_registration.factory, _EVENT)])


class Test_dispatchSubscriptionAdapterRegistrationEvent(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.registry \
            import dispatchSubscriptionAdapterRegistrationEvent
        return dispatchSubscriptionAdapterRegistrationEvent(*args, **kw)

    def test_it(self):
        from guillotina.component import registry
        class _Registration(object):
            def factory(self, *args, **kw):
                pass
        _registration = _Registration()
        _EVENT = object()
        _handled = []
        def _handle(*args):
            _handled.append(args)
        with _Monkey(registry, handle=_handle):
            self._callFUT(_registration, _EVENT)
        self.assertEqual(_handled, [(_registration.factory, _EVENT)])


class Test_dispatchHandlerRegistrationEvent(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.registry import dispatchHandlerRegistrationEvent
        return dispatchHandlerRegistrationEvent(*args, **kw)

    def test_it(self):
        from guillotina.component import registry
        class _Registration(object):
            def handler(self, *args, **kw):
                pass
        _registration = _Registration()
        _EVENT = object()
        _handled = []
        def _handle(*args):
            _handled.append(args)
        with _Monkey(registry, handle=_handle):
            self._callFUT(_registration, _EVENT)
        self.assertEqual(_handled, [(_registration.handler, _EVENT)])


class _Monkey(object):
    # context-manager for replacing module names in the scope of a test.
    def __init__(self, module, **kw):
        self.module = module
        self.to_restore = dict([(key, getattr(module, key)) for key in kw])
        for key, value in kw.items():
            setattr(module, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, value in self.to_restore.items():
            setattr(self.module, key, value)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_dispatchUtilityRegistrationEvent),
        unittest.makeSuite(Test_dispatchAdapterRegistrationEvent),
        unittest.makeSuite(Test_dispatchSubscriptionAdapterRegistrationEvent),
        unittest.makeSuite(Test_dispatchHandlerRegistrationEvent),
    ))
