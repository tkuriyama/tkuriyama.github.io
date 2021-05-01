---
layout: post
title:  "Generating Fractal Trees"
date:   2021-05-01 08:00:00 -0500
tags:   elm art trees
---

Fractal trees are a cool example of simple patterns yielding results with visual appeal and complexity.

The simple version discussed here is materially similar to those found on [Rosetta Code](https://rosettacode.org/wiki/Fractal_tree).

There are two ideas at play:

1. a tree is a series of branches (starting with a trunk and two branches, and recursively calling the algorithm on each of the branches as trunks)
2. the branches are colored increasingly green (`rgb 0 255/level 0`, where the highest layer of the tree has level of 1)

Notice that there are no leaves per se! The naive color scheme generally works well to form the impression of leaves, so long as there are sufficient number of levels in the tree.


With some basic additional logic to gradualyl adjust branch height and width, we have something like this:

![Treemap Version 1](/assets/img/tree1.png){:class="img-responsive"}


## Smoothing Joints

One problem we note is that the narrowing the branch width leads to ragged joints:

![Tree Joint Closeup](/assets/img/tree_detail1.png){:class="img-responsive"}

We could draw triangles to smooth out the joints, or just extend the trunk a bit further

![Treemap Version 2](/assets/img/tree2.png){:class="img-responsive"}


## Generative Appeal

With at most 14 levels, there are (at most) ~16K branches. Adding options to tweak the starting width, height, angles, as well as width change, height change, and the option to add noise, there's plenty of expressivity to generate very different trees.

A wider and fuller example:

![Treemap Version 3](/assets/img/tree3.png){:class="img-responsive"}

A taller and skinnier example:

![Treemap Version 4](/assets/img/tree4.png){:class="img-responsive"}

The leaves for the most part don't look **too** green, even with naive `rgb 0 255 0` at the higest level, thanks to the presence of many smaller branches that provide darker shades of green.


## Links

The above examples were generated in Elm. The actual implementation is a bit more complicated than the Rosetta Code examples, due to wrapping the tree in a `Random.Generator` to add noise.

- [GitHub](https://github.com/tkuriyama/fractaltree-generator)
- [Live Example](https://tarokuriyama.com/fractaltree/)

