---
layout: post
title:  "Taxonomies are Hard"
date:   2021-08-26 13:00:00 -0500
tags:   elm
---

In almost every job I've had, there's been a formal or informal requirement to build a taxonomy. This could be a simple as a set of labels in a spreadsheet, or as formal as a database schema that feeds some catalog of critical assets. 

The same problem arises regularly in software design. In functional programming, in some sense, it arises every time a custom type is designed and pattern matching is required. As a trivial example, I recently worked on a very small app to [compare ukulele strings](https://tarokuriyama.com/ukestrings/).

There is a small set of features that describe sets of strings, one of which is color. So: what should the type of color be? What values are allowed?

## What's the Color

A simple answer is to make color super expressive -- just use, say. RGB!

That would definitely allow maximum correctness. On the other hand... what is the RGB color of that white nylon string set from Aquila? Also... what will users do if they want to filter by, say, white strings?

So while potentailly correct, RGB turns out to be not a very practical or useful choice.

Ok, well, let's pick some practical colors. How about clear, white, and black? That covers fluorocarbon and typical nylon colors, right?

But... Aquila has the Red series, and aNueNue has Purple Aurora, and a bunch of composites are, like, clear with color tinges.

So maybe we should enumerate the standard colors?>

White, Black, Red, Blue, Green, Yellow, Purple, Brown. Grey... is that enough? But wait, there are no Blue or Yellow or Grey strings in the dataset at the moment. There could be some on the market, though. Also, are Worth Browns really brown, or do they look pretty much like Fremont Blacklines?

Hmmm...


## Evaluation Criteria

Picking a color is zooming in on the most granular part of a taxonomy, or a classification system, but it's illustrative of the problems that arise just about every single time, at every level of the data hierarchy. And practitioners know that poor choices, unfortunately, compound.

So what are some evaluation criteria to follow when desining such a system of data?

1. It should be **complete**: one should be able to honestly label every single item that calls for a label, even if it means using a wildcard, or "other" (more on this later). Note that **non-overlapping** complements the completeness; from the producer's perspective, they are equivalent problems.

2. It should be reasonably **useful**: if there are too many choices, or overly esoteric ones, users will be baffled. This is mostly about the consumer perspective.

3. It should be **practical**: assuming the labelling cannot be purely systematic / automated, deciding on the label should be possible by a human following some simple rules. This is mostly about the producer's perspective.


## No Sacred Rules

Keeping the evaluation criteria in mind, what is the type of ukuelel strings colors?

```elm
type StringColor
    = Clear
    | Light
    | Dark
    | Other
```

Hmm... don't light and dark pretty much divide the world between themselves? Clear is a subset of light, right, breaking the rule of no overlaps?

It's a valid point, and in some contexts, one might split the type into two: light vs dark as a higher level filter, with the additional (optional?) choice to specify colors like clear (though, is clear really a color?).

In this context, though, the choice is made based on the audience. To ukulele players who have tried at least a few sets of strings, it's relatively obvious that there are clear and dark fluorocarbon strings, as well as light and dark nylon strings, plus a handful of other colors out there. (Well, other materials and colors, but material is its own feature.)

So it is both useful and practical. It is complete (by definition, since ther eise the `Other` option), and the overlaps are relatively easy to distinguish.

It's still far from perfect, though. For example, 33 of the 184 items in the dataset have color `Other`, some of which are really a mix of `Clear` and `Other` (like clear fluorocarbon with a colored tinge). Those are accepted because they are relatively few in number, but a greater number would merit further reworking of the data type.

Perhaps there are useful evaluation criteria, but no sacred rules.


## Designing a Taxonomy

Given the amount of detail in reality, all models are imperfect, but some are more useful than others.

There are some table stakes for good design:

- thoughtful, detailed, data-based consideration of the entire problem space (as much as practical)
- evaluation based on (non-overlapping) completeness, usefuless, and practicality

Additionally, I've found it's helpful to have one more of the following:

- (appropriate degree of) user input on design choices
- user testing ("is it useful? does it make sense?")
- producer testing ("is it practical? are the labels as expected by the designer?")

Finally, most systems change over time, posing questions like:

- is it easy to change the data design? how do changes propage throughout the system?
- if the data design changes, how difficult is it to migrate the existing data to the new schema?
- are there metrics in place to monitor the health of the data system? (e.g. proliferation of `Other` is an easy red flag)

Maybe that's getting into the implementation and use of a taxonomy (as opposed to purely its design), but usch practical considerations are difficult to ignore in the real world.

There is, maybe, as much art in the design of a good taxonomy as there is science.
