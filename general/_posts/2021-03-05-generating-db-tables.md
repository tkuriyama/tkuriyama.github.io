---
layout: post
title:  "Generating Sqlite Tables with Python"
date:   2021-03-05 09:00:00 -0500
tags:   python sqlite database mypy
---

In Haskell's [persistent](https://www.yesodweb.com/book/persistent) library, one defines database tables with Haskell algebraic data types (or something very close to it, in Template Haskell). The `persisten` library then takes care of setting up tables in the backend, and the programmer enjoys the advantage of having access to the native data types. (`peristent` has other cool features, like automatic data migration on certain schema changes, if you ask it to do so.)

I recently scripted my own version of that approach in Python, after a whole series of unhelpful Foreign Key-related error messages in Sqlite, which don't precise *which* constraint is throwing the error, leading to lots of trial and error, table schema rewrites, etc. Some of the pain may have been mitigaged by better tooling -- as I was only using the Sqlite shell.

(Incidentally, I didn't even realize foreign keys were **not working** until recently... the constraint needs to be manually enabled per database connection: `PRAGMA Foreign_Keys = 1`!)

With `typing`, it's possible to write schema specs that are reasonably expressive. The root of a table schema is a `TypedDict`, with [various supporting type aliases](https://github.com/tkuriyama/datautils/blob/master/datautils/internal/db_sqlite.py):

```python
class TableDef(TypedDict):
    if_not_exists: bool
    name: Name
    cols: List[SchemaCol]
    fks: List[SchemaForeignKey]
    pk: List[Col]
    uniq: List[Col]
```

Some example table definitions would then look like:

```python
country: TableDef = {
    'if_not_exists': True,
    'name': 'Country',
    'cols': [('id', DType.INTEGER, True, False, False),
             ('short', DType.TEXT, False, True, True),
             ('long', DType.TEXT, False, False, False)],
    'fks': [],
    'pk': [],
    'uniq': []
}


holidays: TableDef = {
    'if_not_exists': True,
    'name': 'Holidays',
    'cols': [('id', DType.INTEGER, True, False, False),
             ('date', DType.TEXT, False, False, True),
             ('type', DType.TEXT, False, False, True),
             ('country', DType.TEXT, False, False, False)],
    'fks': [{'cols': ['type'],
             'ref_table': 'HolidayType', 'ref_cols': ['type']},
            {'cols': ['country'],
             'ref_table': 'Country', 'ref_cols': ['short']}],
    'pk': [],
    'uniq': ['date', 'type', 'country']
}
```

There are a few key disadvantages to this approach:

- only a subset of the Sqlite spec is supported
- the map from (TableDef -> SQL create table string) may be buggy

On the other hand, the advantages:

- it's easy to update and regenerate schemas
- it's easy to add additional logic around table creation, like index creation and initial data population
- the schema is available as native Python data (e.g. if type checking or casting is desired, particularly in a weakly typed system like Sqlite)

Translating the above schema for `holidays` into a `CREATE TABLE` and `CREATE INDEX` statement yields:

```sql
CREATE TABLE IF NOT EXISTS Holidays(id INTEGER PRIMARY KEY,
date TEXT NOT NULL,
type TEXT NOT NULL,
country TEXT,
FOREIGN KEY(type) REFERENCES HolidayType(type),
FOREIGN KEY(country) REFERENCES Country(short),
UNIQUE(date, type, country)
);
CREATE INDEX IF NOT EXISTS Holidays_Index
ON Holidays(date, type, country);
```

On the whole, the additional abstraction layer seems to be worthwhile when only basic Sqlite functionality is required. A small step on the elusive quest for minimizing friction across data boundaries...

([Code on GitHub](https://github.com/tkuriyama/datautils/blob/master/datautils/internal/db_sqlite.py))
