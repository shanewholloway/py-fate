# -*- coding: utf-8 -*- vim: set ts=4 sw=4 expandtab
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2013  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
"""
For futures and promises {then:, resolve:, reject:} must always be fully bound closures.
"""
import itertools
from functools import partial

class PromiseApi(object):
    def always(self, fn): return self.then(fn, fn)
    def fail(self, failure): return self.then(None, failure)
    def done(self, success): return self.then(success, None)
    def thenLog(self, **kw): return thenLog(self, **kw)

def isPromise(tgt):
    return (tgt is not None and
        getattr(tgt, 'promise', None) is not None and
        callable(getattr(tgt.promise, 'then', None)))
PromiseApi.isPromise = isPromise

class Promise(PromiseApi):
    def __init__(self, then):
        if then is not None: self.then = then
    promise = property(lambda self: self)
    state = property(lambda self: self.then.state)

def asPromise(tgt):
    if tgt is None or getattr(klass,'promise',None) is None:
        tgt = Future.resolved(tgt)
    return tgt.promise
Promise.wrap = staticmethod(asPromise)

def when(klass, tgt, success=None, failure=None):
    if success is None and failure is None:
        return klass.wrap(tgt)
    return klass.wrap(tgt).then(success, failure)
Promise.when = classmethod(when)
_when = when; when = Promise.when

class Future(PromiseApi):
    def __init__(self, then, resolve=None, reject=None):
        if then is not None:
            self.promise = Promise(then)
        if resolve is not None: self.resolve = resolve
        if reject is not None: self.reject = reject
    then = property(lambda self: self.promise.then)
    state = property(lambda self: self.promise.state)
    def resolve(self, result=None): pass
    def reject(self, error=None): pass

    @classmethod
    def onActionError(klass, err):
        sys.excepthook(*sys.exc_info())

Future.absentTail = Future(None)

#~ Future: thenable, deferred, resolved and rejected ~~~~~~~

def thenable(klass, success=None, failure=None, inner=None):
    if success is not None and not callable(success):
        success, failure = klass._unpack(success, failure)
    if success is None and failure is None:
        return klass.deferred()

    inner = [inner]
    def then(success=None, failure=None):
        if inner[0] is None:
            inner[0] = klass.deferred()
        return inner[0].then(success, failure)
    then.state = None
    def resolve(*args, **kw):
        then.state = True
        tail = inner[0] or klass.absentTail
        if success is not None:
            try:
                res = success(*args, **kw)
                if res is not None:
                    args = (res,); kw={}
            except Exception as err:
                del success, failure
                inner[0] = klass.rejected(err)
                return tail.reject(err)
        del success, failure
        inner[0] = klass.resolved(*args, **kw)
        return tail.resolve(*args, **kw)
    def reject(*args, **kw):
        then.state = False
        tail = inner[0] or klass.absentTail
        if failure is not None:
            try:
                res = failure(*args, **kw)
                if res is not None:
                    args = (res,); kw={}
            except Exception as err:
                args = (err,); kw={}
        del success, failure
        inner[0] = klass.rejected(*args, **kw)
        return tail.reject(*args, **kw)

    return klass(then, resolve, reject)
Future.thenable = classmethod(thenable)
_thenable = thenable; thenable = Future.thenable

def unpackThenable(klass, obj, failure=None):
    success = getattr(obj, 'success', None) or getattr(obj, 'resolve', None)
    if failure is None:
        failure = getattr(obj, 'failure', None) or getattr(obj, 'reject', None)
    return success, failure
Future._unpack = classmethod(unpackThenable)

def deferred(klass):
    actions = []
    inner = [None]
    def then(success=None, failure=None):
        if inner[0] is None:
            f = klass.thenable(success, failure)
            actions.append(f)
            return f.promise
        else: return inner[0].then(success, failure)
    def resolve(*args, **kw):
        then.state = True
        inner[0] = klass.resolved(*args, **kw)
        for ea in actions:
            try: ea.resolve(*args, **kw)
            except Exception as err:
                klass.onActionError(err)
        del actions
    def reject(*args, **kw):
        then.state = False
        inner[0] = klass.rejected(*args, **kw)
        for ea in actions:
            try: ea.reject(*args, **kw)
            except Exception as err:
                klass.onActionError(err)
        del actions
    return Future(then, resolve, reject)
Future.deferred = classmethod(deferred)
_deferred = deferred; deferred = Future.deferred

def resolved(klass, *args, **kw):
    def then(success=None, failure=None):
        ans = klass.thenable(success, failure)
        ans.resolve(*args, **kw)
        return ans.promise
    then.state = True
    return Future(then)
Future.resolved = classmethod(resolved)
_resolved = resolved; resolved = Future.resolved

def rejected(klass, *args, **kw):
    def then(success=None, failure=None):
        ans = klass.thenable(success, failure)
        ans.reject(*args, **kw)
        return ans.promise
    then.state = False
    return Future(then)
Future.rejected = classmethod(rejected)
_rejected = rejected; rejected = Future.rejected

def inverted(klass, tgt=None):
    if tgt is None: tgt = klass.deferred()
    return Future(tgt.then, tgt.reject, tgt.resolve)
Future.inverted = classmethod(inverted)
_inverted = inverted; inverted = Future.inverted

def thenLog(tgt, **kw):
    if kw.get('showArgs', True):
        def log(key,*a,**k):
            key = kw.get(key, key)
            if kw: print '%s: %r %r'  % (key,a,k)
            else: print '%s: %r' % (key, a)
    else:
        def log(key): print kw.get(key, key)
    tgt.promise.then(partial(log, 'success'), partial(log, 'failure'))
    return tgt

#~ Compositions: any, all, every, first ~~~~~~~~~~~~~~~~~~~~
def forEachPromise(iterable, step):
    n = 0; i = itertools.count()
    for ea in iterable:
        n+=1
        if not isPromise(tgt):
            step(True, i.next(), n)
        else: tgt.promise.then(
            lambda *a,**k: step(True, i.next(), n),
            lambda *a,**k: step(False, i.next(), n))
    if n<0: step(True, 0, n)

def every(iterable):
    future = deferred(); future.state = True
    def step(state, i, n):
        future.state = future.state and state
        if i<n: return
        elif future.state:
            future.resolve((i,n))
        else: future.reject((i,n))
    forEachPromise(iterable, step)
    return future.promise
Future.every = Promise.every = classmethod(every)

def all(iterable):
    future = deferred()
    def step(state, i, n):
        if not state: future.reject((i,n))
        elif i>=n: future.resolve((i,n))
    forEachPromise(iterable, step)
    return future.promise
Future.all = Promise.all = classmethod(all)

def first(iterable):
    future = deferred()
    def step(state, i, n):
        if state: future.resolve((i,n))
        else: future.reject((i,n))
    forEachPromise(iterable, step)
    return future.promise
Future.first = Promise.first = classmethod(first)

def any(iterable):
    future = deferred()
    def step(state, i, n):
        if state: future.resolve((i,n))
        elif i>=n: future.reject((i,n))
    forEachPromise(iterable, step)
    return future.promise
Future.any = Promise.any = classmethod(any)

