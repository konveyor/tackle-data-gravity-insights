# pylint: disable=invalid-name,missing-function-docstring,not-callable,unnecessary-lambda
################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""
Peg Module
"""

# This code needs major cleanup! I am disabling the PyLint messages
# until we can get someone to fix them properly. This code is an example
# of how critical it is to use a good linter at the start of a project!


def pegop(f):
    def g(*args):
        memo = [None] * 64

        def h(s):
            i = hash(s) % 64
            if memo[i] and memo[i][0] == s:
                return memo[i][1]

            v = f(s, *args)
            memo[i] = (s, v)
            return v

        return h

    return g


def pegcxt(f):
    def g(e):
        c = []
        c.append(f(e, lambda s: c[0](s)))
        return c[0]

    return g


@pegop
def choice(s, *args):
    for f in args:
        a = f(s)
        if a != ():
            return a
    return ()


@pegop
def seq(s, *args):
    r = []
    for f in args:
        a = f(s)
        if a == ():
            return ()
        s = a[0]
        r += a[1]
    return s, r


@pegop
def val(s, x):
    if s.startswith(x):
        return s[len(x):], []
    return ()


@pegop
def before(s, *args):
    t = None
    for a in args:
        if a is None:
            t = "" if t is None else t
        elif a in s and (t is None or (len(s) - s.index(a)) > len(t)):
            t = s[s.index(a):]
    if t is None:
        return ()
    return t, []


@pegop
def match(s, e, r=None):
    a = e(s)
    if a == ():
        return ()
    if r is None:
        return a[0], a[1] + [s[: len(s) - len(a[0])]]
    return a[0], r(a[1], s[: len(s) - len(a[0])])


@pegop
def debug(s, e):
    print("debug:", s)
    return e(s)


def nil(s):
    return s, []


def star(e):
    f = choice(seq(e, lambda s: f(s)), nil)
    return f
