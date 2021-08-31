---
layout: post
title:  "JavaScript in 10 Days: Day 1"
date:   2021-08-31 09:00:00 -0500
tags:   javascript typescript
---

In 1995, Brandon Eich developed the first version of JavaScript for Netscape in 10 days (during which, Eich notes, he didn't sleep very much).

For the past decade, as I've pursued different parts of computer science and programming as a hobby, I've largely seen JavaScript as a necessary evil, mostly avoiding it unless strictly necessary. It occurs to me that such an approach doesn't accord well with my belief in first principles, so I'm spending 10 days to start to fix it.

Having worked with Elm for over a year, and hearing a great deal of speculation and discussion of what goes on behind the scenes in the Elm-to-JavaScript compiler, I'm also sufficiently motivated by curiosity.


## The Plan

As of now, my plan is:

- watch some talks and/or read some articles, maybe one a day
- pick up the fundamentals from Douglas Crockford's [JavaScript, the Good Parts](https://www.oreilly.com/library/view/javascript-the-good/9780596517748/), which seems to be a standard (albeit missing more recent developments)
- learn a modern development and build pipeline for emacs (probably Typescript flavored)
- work through Luis Atencio's [The Joy of Javacript](https://www.manning.com/books/the-joy-of-javascript); this was recommended by a trusted source and the functionally oriented introduction seems promising

That probably doesn't cover very much of the JavaScript ecosystem, from evolving language standards, to compiler optimizations, to popular frameworks like React and Vue, to things like webpack... 


## Setup emacs

I haven't adopted language servers in emacs yet, so these seem to be the other standard packages (installed with standard configs from the README pages):

- [`typescript-mode`](https://github.com/emacs-typescript/typescript.el)
- [`ts-comint`](https://github.com/emacs-typescript/ts-comint)
- [`tide`](https://github.com/ananthakumaran/tide/)

I already had node v16 and had no problems installing `tsun` (the REPL used by `ts-comint`, per the repo README).

The internet also says that Visual Studio has excellent support for TypeScript (as it seems to have for many languages these days).


## Day 1 Talks / Articles

- Brandon Eich, [A Brief History of JavaScript](https://www.youtube.com/watch?v=GxouWy-ZE80)

A very short talk, my main takeaway is that there is a healthy, well-considered, structured approach to the development of language standards, which has been refined over many years of struggle.

The approach of "break the language down into orthogonal primitives that work well together" makes a lot of sense as a language committee's goal.



## TypeScript Intro

[TypeScript for Functional Programmers](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes-func.html)

- Structural typing is a new concept, coming from Haskell and Elm. It seems like something worth careful consideration as a source of unexpected data / type widening.

- The implementation of discriminated unions is... interesting? It seems simple enough, though it would appear that the temptation to use nested discriminants in type narrowing represents false hope.


## JavaScript, the Good Parts


**Chapter 2 Grammar**

- "If you want to learn more about the bad parts and how to use them badly, consult any other JavaScript book."


**Chapter 3 Objects**

- The dynamic nature of the prototype chain seems powerful and a potential source of confusion...

- The global single variable namespacing trick no longer seems to be as relevant with the introduction of modules in [ES6](https://www.w3schools.com/js/js_es6.asp)([MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)).


**Chapter 4 Functions**

- The "function invocation pattern" has surely been obviated by updated language implementation in subsequent versions..?

**Chapter 5 Inheritance**

- This chapter is a bit confusing. I can see why many languages proudly advertie that "there is only one way to do things". Fortunately, Atencio covers the topic with a more modern perspective early in his book.


## The Joy of Javascript (JoJ)

**Chapter 2 Inheritance-Based Object Modeling**

- Mantra: always remember to use the `new` keyword for constructors; the following provides defensive code (new in ESMA 20215?)

```javascript
if (!new.target) {
   return new HashTransaction(sender, recipient);
}
```

- JavaScript allows prototypal inheritance, constructor functions, and more recently classes
- prototypal inheritance is an oxymoron; remember that classes are syntactic sugar for smoothing over prototype configuration

## JoJ Code

[Day 1 Code](https://github.com/tkuriyama/learn-js/tree/master/joj/day1/src)

It took a while to figure out how to independently compile the Chapter 2 final class-based example.

- copy the `.rc` files from the [JoJ repo](https://github.com/JoyOfJavaScript?language=javascript)
- follow installation instructions for babel
- install a bunch of missing plugins (based on babel errors): `npm install --save-dev @babel/...`
- add some missing plugins to the [`.babelrc` file](https://github.com/tkuriyama/learn-js/tree/master/joj)

Finally, run: 

```node
% npx babel day1/src --out-dir day1/lib
```

And, since I added a `console.log` to the source:

```node
% node txns.js                                                                                    (master)learn-js
64284210552842720: Transaction from luis@tjoj.com to luke@tjoj.com fo
```

## Other Code

[Day 1 Code](https://github.com/tkuriyama/learn-js/tree/master/snippets/day1)

Other than code examples from the JoJ, I mostly wrote `hello_world`-esque TypeScript to get familiar with very basic functions and type annotations, like three flavors of fibonacci (naive recursive, efficient recursive, memoization with array).

Here is the Tower of Honoi, lifted from a previous Haskell implementation. It took me a while to decipher the typescript error, which ultimately wanted the `(p1, p2)` tuple syntax to be `[p1, p2]`.

```typescript
type Peg = string

type Move = [Peg, Peg]

function hanoi(n: number, p1: Peg, p2: Peg, p3: Peg): Move[] {
    if (n === 0) {
        return []
    }
    else {
        return hanoi(n - 1, p1, p3, p2).concat(
            [[p1, p2]],
            hanoi(n - 1, p3, p2, p1)
        )
    }
}
```


## Todo / To Read

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- Compiling with both TypeScript with Babel
- More chapters of Crockford and Atencio
- [Eloquent JavaScript](https://eloquentjavascript.net/) has exercises at the end of chapters, which might be worth exploring
- Kyle Simpson, [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS/tree/1st-ed)
- Atencio: [Shadowing](http://mng.bz/OEmR)
- Atencio: "...proposals related to private class fields (http://mng.bz/YqVB) and static fields (http://mng.bz/5jgB)..."
