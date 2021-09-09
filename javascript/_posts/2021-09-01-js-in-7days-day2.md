---
layout: post
title:  "JavaScript in 10 Days: Day 2"
date:   2021-09-01 18:00:00 -0500
tags:   javascript typescript archive
---

Today's plan is to get through the TypeScript handbook and to skim as much of Crockford as possible, as there seem to be many things in the Crockford that are no longer applicable.

## More emacs Setup

For getting started with editing pure JavaScript files, I followed [this page](https://emacs.cafe/emacs/javascript/setup/2017/04/23/emacs-setup-javascript.html) and looked at one or two others.
- `js2-mode`
- `js2-refactor`
- `xref-js2` and `ag`

The emacs setup is always a bit tricky, since I don't have a very good knowledge of elisp and things like `use-package` syntax. [This version](https://gist.github.com/tkuriyama/9dc372fdf7069744e3def37a6c8f8087) seems to work as a starting point.


## Day 2 Talks / Articles

Articles referenced by Atencio on [shadowing](http://mng.bz/OEmR), [private class fields](http://mng.bz/YqVB), [static fields](http://mng.bz/5jgB)


## TypeScript Handbook

[The TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)

**The Basics**

- To compile  a specifc file, run `tsc` with flags and filename.
- To compile with `tsconfig.json`, run `tsc` alone in directory with source code (where the tsconfig file denotes the root of a project)
- the [tsconfig handbook](https://www.typescriptlang.org/tsconfig)

**Everyday Types**

- Optional object properties are specified by adding a `?` after the property name (instead of e.g. wrapping the type in a `Maybe`)

- The optional flag can also be used by accessors: `console.log(obj.last?.toUpperCase());`

- Interfaces: similar to type aliases, but properties are extensible

- Type assertions: `const myCanvas = document.getElementById("main_canvas") as HTMLCanvasElement;` or `const myCanvas = <HTMLCanvasElement>document.getElementById("main_canvas");`

- Literal types -- string, number, and boolean; also can assert type `as const`

- Adding `!` after a variable asserts that its type is non-null

- Enums: TypeScript only ([guide](https://www.typescriptlang.org/docs/handbook/enums.html))

**Narrowing**



**More on Functions**

- Call signatures for functions that have properties (!)

- Constructor signatures are specified with a `new` keyword in front of a call signature

- Generics: need to specify a type parameter in `<>`: `function firstElement<Type>(arr: Type[]): Type`

- Constraints -- similar to ideas of type classes or extensible records `function longest<Type extends { length: number }>(a: Type, b: Type) {`

- Parameter defaults can be specified

- Rest parameters with `...` syntax; same for rest arguments

- Parameter destructuring

**Object Types**

- can combine destructring patterns for parameters with default values

- `readonly` keyword for properties (a bit like `const` the referent can still change, but the reference cannot be written to)

- index signatures
- interfaces can be extended `extends`; they can be intersected `&` (err... but his is actually a union of all the properties?)

- interfaces can take a type parameter...

- `ReadOnlyArray`, no constrctor: `const roArray: ReadonlyArray<string> = ["red", "green", "blue"];`

- tuples also support optional and rest parameters, readonly


**Type Manipulation**

- Generic interfaces and classes, can build constraints with `extends`; class types can be used in generics (see [mixins](https://www.typescriptlang.org/docs/handbook/mixins.html) too)

- `keyof` takes an object and returns union of its keys

- `typeof` can be used on identifiers or their properties
- indexed access type to look up property of another type (when is this useful?)

- conditional types -- use ternary conditional expression in types

- mapped types: generic type with union of PropertyKeys (often with `keyof`)

- template literal types, instrinstic string manipulation types...

**Classes**

- `!` -- definite assignment assertion used after class field name
- readonly -- limits assignemnt to the constructor

- visibility: `public`, `protected`, `private`

**Modules**

- `export{};` makes a file a module without imports or exports



## JavaScript, the Good Parts

**Chapter 6 Arrays -> Appendix B**

Skimmed the chapters.

- sorting is coerced to strings by default; provide comparison function to sort eg numbers `function (a, b) { return a - b }`

- the appendices A & B are maybe the most interesting parts of the book!


## JoJ

None.

## JoJ Code
None.


## Other Code

I looked at the [Eloquent JavaScript](https://eloquentjavascript.net/) higher-order functions part and decided to write some standard cons list and map / folds.

Here is a cons list in the usual formulation, with constructors, using generic type parameters:

```typescript
type ConsList<T> =
    null |
    [T, ConsList<T>]

function cons<T>(head: T, tail: ConsList<T>): ConsList<T> {
    return [head, tail];
}

function fromArray<T>(arr: Array<T>): ConsList<T> {
    let xs: ConsList<T> = null;
    for (let i = arr.length - 1; i >= 0; i--) {
        xs = cons(arr[i], xs)
    }
    return xs;
}
```

Here is `foldr` with the same implementation as Haskell:

```typescript
function foldR<T, U>(
    f: ((x: T, acc: U) => U),
    acc: U,
    xs: ConsList<T>): U {

    if (xs === null) {
        return acc;
    }
    else {
        let [h, t] = xs
        return f(h, foldR(f, acc, t));
    }
}
```

Now for example `map` can be written with `foldR`:

```typescript
function mapFoldR<T, U>(f: (x: T) => U, xs: ConsList<T>): ConsList<U> {
    let empty = null as ConsList<U>;
    return foldR((a, b) => cons(f(a), b), empty, xs);
}
```

I then got stuck for a very long time trying to figure out a type error:
```typescript
const xs = fromArray([1, 2, 3]);

console.log(map(x => x + 1, xs));

let empty: ConsList[<number> = null;
console.log(foldR((a, b) => cons(a, b), empty, xs)); // ERROR

console.log(mapFoldR(x => x + 1, xs));
```

It took getting a [Stack Overflow answer](https://stackoverflow.com/questions/69020879/type-error-with-generic-conslist-in-typescript) to figure out the error.

```typescript
let empty: ConsList[<number> = null;   // Problem...
let empty = null as ConsList<number>;  // OK
```

In short, the former causes TypeScript to narrow the type too much (to `null` as opposed to `ConsList<number>`. Good to know!

Correcting the type assertion, TypeScript is happy and the output is also as expected:

```javascript
% node fold.js
[ 2, [ 3, [ 4, null ] ] ]    // map (+1)
[ 1, [ 2, [ 3, null ] ] ]    // foldr with cons
[ 2, [ 3, [ 4, null ] ] ]    // map (+1) with foldR
```


## Wrapping Up
[Day 2 Code](https://github.com/tkuriyama/learn-js/tree/master/snippets/day2)


Is TypeScript what happens when static-typing / functional programming concepts are applied to an inherently impure, dynamic language? It's messy and there are many more ways (too many?) to do things, but it's also more approachable (there is hardly any theory in the TypeScript handbook, unlike in any Haskell introduction). 

With such tooling, it seems like consistent conventions and domain-specific best practices play should play a greater rol in producing scalable, reusable, correct code. 

It's very different from, say, the opinionated minimalism of Elm (oh, you want tuples longer than three? nah... you shouldn't really use them).

As for Crockford's book, I'm not sure I'd recommend it to someone in my position, as there are undoubtedly more modern alterantive out there. The appendices on awful and bad parts of the language are interesting, though.


## Todo / To Read

- ~~[TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)~~
- Compiling with both TypeScript with Babel
- More chapters of ~~Crockford~~ and Atencio
- [Eloquent JavaScript](https://eloquentjavascript.net/) has exercises at the end of chapters, which might be worth exploring
- Kyle Simpson, [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS/tree/1st-ed)
- ~~Atencio: [Shadowing](http://mng.bz/OEmR)~~
- ~~Atencio: "...proposals related to private class fields (http://mng.bz/YqVB) and static fields (http://mng.bz/5jgB)..."~~
- Figure out how to use `outDir`(?) to compile `.js` files to separate subdirectory
