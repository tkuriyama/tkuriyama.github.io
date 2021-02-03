---
layout: post
title:  "Types with Python3 and Mypy"
date:   2021-02-02 13:00:00 -0500
tags:   python mypy
---

As I started to rewrite and aggregate a variety of old Python scripts for working with data, it seemed like a good time to learn the latest in Python3's support for types.

The area still appears to be in active development, so I started a fresh `virtualenv` with Python 3.9.1. (`poetry` seems to be gaining in popularity these days, but I stuck with what I had, so as to not change too many things at once.)

## Type Annotations and ADTs

[`typing`](https://docs.python.org/3/library/typing.html#module-typing) adds support for type annotations in the Python standard library since version 3.5. Beyond type annotations, there are now some additional tools for type expressivity, including type aliases, union types, generics, etc.

With Unions and Tuples, it seems possible to define data in a similar way as Algebraic Data Types from functional languages...

For example, in Haskell we often see a simple ADT like this:

```haskell
data Status = OK | Error String
```

One attempt to translate it might yield something like: 

```python
class Code(Enum):
    OK = 0
    ERROR = 1

Status = Status = Union[Code, Tuple[Code, str]]
```

... where the lack of data constructors make the meaning of Status far more ambiguous.

This is slightly better (with `show` defined a bit like a typeclass definition in Haskell), though it still invites a construction like `Status(Code.OK, "some ok message")`, which is not intended:

```python
class Status():
    def __init__(self, code: Code, error_msg : Optional[Exception] = None):
        self.code = code
        self.error_msg = error_msg
    def show(self) -> str:
        c = 'OK' if self.code is Code.OK else 'Error'
        return c + '' if not self.error_msg else ': {}'.format(self.error_msg)
```

`dataclass` is new in Python 3.7 and helps resolve the problem of constructors. [This post](http://blog.ezyang.com/2020/10/idiomatic-algebraic-data-types-in-python-with-dataclasses-and-union/) shows how to define a very similar data type.

The `dataclass` decorator applies magic of auto-generating constructors, as well as some other things. In this case, we set `frozen=True` to avoid mutation of generated Status objects, and we also want the equaltity comparison that `dataclass` gives us by default.

```python
`
@dataclass(frozen=True)
class OK:
    msg: str = "OK"

@dataclass(frozen=True)
class Error:
    msg: str

Status = Union[OK, Error]
```

That's much more concise and directly expresses the intent! (There is still the problem of needing a constructor argument for `OK()`, but the default value is a reasonable workaround.)

## Type Checking

So we can write more expressive code (which also, I think, obviates the need for much of the traditional, docstring argument comments in Python). But how do we type check?

- Google has [`pytype`](https://github.com/google/pytype) but it doesn't appear to work with Python >3.7 yet
- Microsoft has [`pyright`](https://github.com/microsoft/pyright)
- `mypy` seems to one of the most mainstream libraries, used by Dropbox etc

I went with `mypy`, with the added benefit that it was easy to integrate with `flycheck` in emacs.

Using the `Status` type now looks like this:

```python
def close(conn: Conn) -> Status:
    """Close DB connection object."""
    try:
        conn.close()
        status = OK()
    except Exception as e:
        status = Error(str(e))
    return status
```

... where the `status` variable is the return type of `Status`, right?

It turns out that the above does not type check with `mypy` yielding `Incompatible types in assignment (expression has type "Error", variable has type "OK") (python-mypy)`. 

The [`type inference`](https://mypy.readthedocs.io/en/stable/type_inference_and_annotations.html) section of the docs say:

*"Mypy considers the initial assignment as the definition of a variable. If you do not explicitly specify the type of the variable, mypy infers the type based on the static type of the value expression..."*

Given that Python variables are generally mutable, that seems pretty reasonable... So we need an explicit type annotation for `status`:

```python
def close(conn: Conn) -> Status:
    """Close DB connection object."""
    status: Status
    try:
        conn.close()
        status = OK()
    except Exception as e:
        status = Error(str(e))
    return status
```

Now that type checks. The result is expressive and still pretty concise. With constructors, though, we want nice deconstructors (to pattern match on different `Status`, say)... which seem to be on the horizon in [`PEP 634`](https://www.python.org/dev/peps/pep-0634/).

<hr>

**Notes**

* I discovered the `mypy` type inference rule from a helpful answer on [SO](https://stackoverflow.com/questions/66016659/unexpected-optional-behavior-with-python3-typing-and-mypy)
