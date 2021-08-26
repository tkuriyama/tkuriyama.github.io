---
layout: post
title:  "Dropdown Menu for Elm UI"
date:   2021-08-22 13:00:00 -0500
tags:   elm
---

I've been looking for a dropdown menu to use with `elm-ui` for a while, and finally came across [this article](https://medium.com/nerd-for-tech/reusable-dropdown-in-elm-with-parameterized-types-part-ii-77f58515a662) recently. The basic approach is adopted directly for the implementation described here.


## Overview

The idea is simple -- a dropdown is either showing a specific item (specifically, no item to start with), or a list of possible items. 

```elm
type Dropdown a
    = ShowItem (Maybe a)
    | SelectItem (List a)
```

Translating the same idea into an `elm-ui` element:

```elm
          E.el
                [ E.width E.fill
                , Border.width 1
                , E.padding 5
                , E.below (viewOptionList options)
                ]
                (E.text selected)
```

This works because of `Element.below`, which prevents the layout from being modified by the dropdown options when the menu is expanded.

From the [`elm-ui` docs](https://package.elm-lang.org/packages/mdgriffith/elm-ui/latest/Element) (which I should have read more carefully before, as it specifically mentions dropdowns...):

```elm
Let's say we want a dropdown menu. Essentially we want to say: put this element below this other element, but don't affect the layout when you do.

Element.row []
    [ Element.el
        [ Element.below (Element.text "I'm below!")
        ]
        (Element.text "I'm normal!")
    ]
```

Other than the actual rendering, a basic dropdown needs two or three messages to be wired through `update`:

1. Select an item
2. Expand the dropdown
3. Clear the selection

Accordingly, the type signature for a generic dropdown looks like this:

```elm

view :
    String
    -> Dropdown a
    -> (a -> String)
    -> msg
    -> (a -> msg)
    -> msg
    -> E.Element msg
view title dropdown toString openMsg clickMsg clearMsg
```


The full implementation is short and [available for reference here](https://github.com/tkuriyama/uke-strings/blob/master/src/UkeStrings/Dropdown.elm).


## Notes

This implementation only stores the current state in the dropdown. So, for example, when a specific item is selected, dropdown has type `ShowItem (Maybe a)` and isn't aware of all its possible options.

While it'd be simple to store all possible options in the dropdown itself, loading the options dynamically when the user expands the dropdown can be cleaner to model, especially if the options should be filtered by other data in the model.

An exampe of multiple dropwdowns that filter different features of shared data is [available here](https://tarokuriyama.com/ukestrings/).


## Tests

From GUI-based testing, a few items emerge:

- The dropdown options can be very many, rendering a long menu; using `scrollbarY` with a fixed height is a good alternative.
- It's natural user behavior to click outside the dropdown menu when it's to indicate a "cancel" action. How should that be supported? (But how to specify a click target that's everything except the dropdown?)
- WHen there are many filters, it can be difficult to identify which filters are selected at a glance, so some visual cues like background coloring are helpful

## Wrapping Up

It turns out that rolling one's own dropdown with `elm-ui` isn't difficult -- at least for something rudimentary that's nonetheless very usable. The most noticeable missing feature is the ability to click outside the dropdown to close it, for which I haven't found a good solution yet..

![Dropdown Menu Screenshot](/assets/img/drodown.png){:class="img-responsive"}

.

## References

- [Reusable dropdown in Elm with parameterized types](https://medium.com/nerd-for-tech/reusable-dropdown-in-elm-with-parameterized-types-part-ii-77f58515a662))
