---
layout: post
title:  "The Random Monad in Elm"
date:   2021-04-23 09:00:00 -0500
tags:   elm haskell
---

Monad is not a word in the Elm lexicon, and I guess there's no reason to talk about it -- other than for familiarity. Having learned some monads (and functors and applicatives) from Haskell, it was be helpful for me to identify familiar equivalents to get started.

To maintain purity, randomness in Elm is created by the Random monad, which is a `Generator` type that tells the runtime to do the dirty work of generating randomness. The Elm app then gets back some (pseudo?)random value from the runtime, which can be used deterministically.

For example, a primitive generator:

```elm
int : Int -> Int -> Generator Int
```

... creates a generator for a random int in given range.

There is a single way to "extract" random values from generators:

```elm
generate : (a -> msg) -> Generator a -> Cmd msg
```

... which takes a constructor, a generator, and returns a `Cmd` from the runtime. 

The example from the [Random module docs](https://package.elm-lang.org/packages/elm/random/latest/Random) is illustrative.

```elm`
point : Random.Generator (Int, Int)
point =
  Random.pair (Random.int -100 100) (Random.int -100 100)

type Msg = NewPoint (Int, Int)

newPoint : Cmd Msg
newPoint =
  Random.generate NewPoint point
  ```


## Applying Random

So let's say we want to use randomness in something a bit more involved -- like dividing a list into n sublists of random length.

One approach is with a fold, taking a list of random elements n times and accumulating them into a list of lists.


```elm

divideList : Int -> List Pair -> Random.Generator (List (List a))
divideList n pairs =
    let
        f i generatorAcc =
            generatorAcc |> Random.andThen (takeRandom i)
    in
    List.range 1 n
        |> List.foldr f (Random.constant ( [], pairs ))
        |> Random.map Tuple.first
```


Here, the fold accumlator is a tuple of (collected sublists, list of remaining elements in original list). Since the accumulator will use Random generators, it needs to be initialized with `Random.constant`, which is the equivalent of `pure` -- the minimal context for the Random monad.
`takeRandom` has type signature: 

```elm
takeRandom :
    Int
    -> ( List (List a), List a )
    -> Random.Generator ( List (List a), List a )
```

... which means we need equivalent of Haskell's `bind` to use it with the monadic accumulator:

```haskell
Control.Monad (=<<) :: Monad m => (a -> m b) -> m a -> m b
```

That's the purpose of `Random.andThen`:

```elm
andThen : (a -> Generator b) -> Generator a -> Generator b
```

Note also that `divideList` uses `Random.map` to extract the first value from the accumulator pair -- equivalent to `fmap`:

```elm
map : (a -> b) -> Generator a -> Generator b
```

The implementation of `takeRandom` uses a generator from [`Random.List.choices`](https://package.elm-lang.org/packages/elm-community/random-extra/latest/Random.List). It is otherwise straightforward: take all remaining elements if it's the last sublist, otherwise accumulate a random number of randomly selected items. 

```elm
takeRandom :
    Int
    -> ( List (List a), List a )
    -> Random.Generator ( List (List a), List a )
takeRandom n ( acc, elems ) =
    if n == 1 then
        Random.constant ( elems :: acc, [] )

    else
        Random.int 1 (maxElems elems n)
            |> Random.andThen
                (\ct -> RL.choices ct elems)
            |> Random.andThen
                (\( xs, ys ) -> Random.constant ( xs :: acc, ys ))

```

(There's probably a nicer way that doesn't involve checking the index / sublist count.)

