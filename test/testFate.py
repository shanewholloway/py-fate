#!/usr/bin/env python
# -*- coding: utf-8 -*- vim: set ts=4 sw=4 expandtab
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2013  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

import contextlib
import unittest, os, sys
sys.path.insert(0, os.path.join(__file__, '../..'))
import fate

class AnswerLog(object):
    def __init__(self, testCase):
        self.testCase = testCase
    i = 0
    def ansLog(self, *a, **k): self.i += 1
    __call__ = ansLog

    def __enter__(self): return self
    def __exit__(self, exc=None, exc_type=None, exc_tb=None): pass

    def assertCalled(self, n, msg="Should have been called N times"):
        return self.testCase.assertEqual(self.i, n, msg)
    def assertAnswered(self, msg="Should have answered"):
        return self.assertCalled(1, msg)
    def assertUnanswered(self, msg="Should NOT have answered"):
        return self.assertCalled(0, msg)

class TestFate(unittest.TestCase):
    def answerLog(self): return AnswerLog(self)

    def testResolved(self):
        f = fate.resolved(42)
        self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f.then(ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.then(success=ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.then(failure=ansLog)
            ansLog.assertUnanswered()

        with self.answerLog() as ansLog:
            f.then(None, ansLog)
            ansLog.assertUnanswered()

        with self.answerLog() as ansLog:
            f.always(ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.done(ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.fail(ansLog)
            ansLog.assertUnanswered()

    def testRejected(self):
        f = fate.rejected(42)
        self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f.then(ansLog)
            ansLog.assertUnanswered()

        with self.answerLog() as ansLog:
            f.then(success=ansLog)
            ansLog.assertUnanswered()

        with self.answerLog() as ansLog:
            f.then(failure=ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.then(None, ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.always(ansLog)
            ansLog.assertAnswered()

        with self.answerLog() as ansLog:
            f.done(ansLog)
            ansLog.assertUnanswered()

        with self.answerLog() as ansLog:
            f.fail(ansLog)
            ansLog.assertAnswered()

    def testThenableResolve(self):
        f = fate.thenable()
        self.assertIsNone(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(ansLog)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(success=ansLog)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(failure=ansLog)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertUnanswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(None, ansLog)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertUnanswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(ansLog, ansLog)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

    def testThenableReject(self):
        f = fate.thenable()
        self.assertIsNone(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(ansLog)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertUnanswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(success=ansLog)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertUnanswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(failure=ansLog)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(None, ansLog)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable(ansLog, ansLog)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

    def testThenableThenResolve(self):
        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(success=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(failure=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertUnanswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(None, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertUnanswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(ansLog, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

    def testThenableThenReject(self):
        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertUnanswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(success=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertUnanswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(failure=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(None, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.thenable()
            f.then(ansLog, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

    def testDeferredResolve(self):
        f = fate.deferred()
        self.assertIsNone(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(success=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(failure=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertUnanswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(None, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertUnanswered()
            self.assertTrue(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(ansLog, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.resolve(42)
            ansLog.assertAnswered()
            self.assertTrue(f.state)

    def testDeferredReject(self):
        f = fate.deferred()
        self.assertIsNone(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertUnanswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(success=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertUnanswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(failure=ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(None, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

        with self.answerLog() as ansLog:
            f = fate.deferred()
            f.then(ansLog, ansLog)
            self.assertIsNone(f.state)
            ansLog.assertUnanswered()
            f.reject(-1942)
            ansLog.assertAnswered()
            self.assertFalse(f.state)

if __name__=='__main__':
    unittest.main()

