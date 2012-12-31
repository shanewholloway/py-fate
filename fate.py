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

class PromiseApi(object):
    def always(self, fn): return self.then(fn, fn)
    def fail(self, failure): return self.then(None, failure)
    def done(self, success): return self.then(success, None)

def isPromise(tgt):
    if tgt is None: return False
    return (getattr(tgt, 'isPromise', bool)() or 
        callable(getattr(tgt, 'then', None)))
PromiseApi.isPromise = isPromise # dual static and normal method
def isFuture(tgt):
    if tgt is None: return False
    return (getattr(tgt, 'isFuture', bool)() or 
        callable(getattr(tgt, 'resolve', None)) or
        callable(getattr(tgt, 'reject', None)))
PromiseApi.isFuture = isFuture # dual static and normal method

class Promise(PromiseApi):
    def __init__(self, then):
        if then is not None: self.then = then
    promise = property(lambda self: self)
    state = property(lambda self: self.then.state)

    @classmethod
    def wrap(klass, tgt):
        if klass.isPromise(tgt): return tgt
        return klass._valueAsPromise(tgt)

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
    if not callable(success):
        success, failure = thenable.unpack(success, failure)
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

def _valueAsPromise(tgt): return Future.resolved(tgt).promise
Promise._valueAsPromise = staticmethod(_valueAsPromise)

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


#~ Compositions: any, all, every, first ~~~~~~~~~~~~~~~~~~~~
"""
function forEachPromise(anArray, thisArg, resolveFirst, rejectFirst, rejectAll) {
  var n=0, future=deferred(thisArg), linchpin={
    push: function(ea) {
      if (isPromise(ea)) {
        ++n; ea.then(linchpin)
      } else if (resolveFirst)
        future.resolve(anArray)
      return ea },
    resolve: function() {
      if (resolveFirst || (--n < 1))
        future.resolve(anArray) },
    reject: function() {
      if (rejectFirst || (--n < 1))
        future.reject(anArray)
      if (rejectAll)
        future.resolve = future.reject } }

  ;[].forEach.call(anArray, linchpin.push)
  if (n<1) future.resolve(n)
  return future }

exports.every = Future.every = Promise.every = every
function every(anArray, thisArg) {
  return forEachPromise(anArray, thisArg, false, false, true) }
exports.all = Future.all = Promise.all = all
function all(anArray, thisArg) {
  return forEachPromise(anArray, thisArg, false, true) }
exports.first = Future.first = Promise.first = first
function first(anArray, thisArg) {
  return forEachPromise(anArray, thisArg, true, true) }
exports.any = Future.any = Promise.any = any
function any(anArray, thisArg) {
  return forEachPromise(anArray, thisArg, true, false) }

"""
