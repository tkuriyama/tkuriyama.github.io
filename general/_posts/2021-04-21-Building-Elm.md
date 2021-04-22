---
layout: post
title:  "Building Elm Projects"
date:   2021-04-21 19:00:00 -0500
tags:   elm
---

The Elm ecosystem is one of the friendliest I've used (from the incredible compiler messages to the friendly folks on Elm Discourse and Slack). It's mature enough now, though, that there are a variety of dev tools that are widely used but not part of the official documentation.

Since I find myself repeating build instructions on GitHub projects, here's an attempto DRY it up for now.


## Standard Build

All Elm projects can be built with [elm make](https://elmprogramming.com/elm-make.html), such as:

````shell
elm make examples/Main.elm --optimize --output=elm.js
```
... which builds the example specified in `examples/Main.elm` and compiles it to elm.js.

Note that all build tools use the `elm.json` configuration file, and any code not in `src` needs to explicitly added under `source-directories` in the file. So, in this case:

```json
"source-directories": [
        "src",
        "examples"
    ],
```


## Optimized Build

There are a variety of tools that can be included in a build piepeline, including tests, formatting, and further optimization, and minification of the generated JavaScript.

I typically use the following packages, which can be installed with `npm` (globally so they work for all Elm projects, or omit the `-g` flag to install locally) like so:

```shell
npm install -g elm-coverage
npm install -g elm-format
npm install -g elm-test
npm install -g elm-optimize-level-2
npm install -g elm-minify
```

Note that `elm-minify` is deprecated, though it works fine for now as a wrapper for `terser`. For an alternative minification, see the [terser command recommended by elm-optimize-level-2](https://github.com/mdgriffith/elm-optimize-level-2/blob/HEAD/notes/minification.md). There are other optimization tools out there, for those inclined to do some research.

Using the above tools, the full build looks like the following, which can be run as a shell script:
```shell
elm-format src/ --yes

# elm-coverage .
elm-test

elm-optimize-level-2 src/Main.elm --output=elm.js

elm-minify elm.js
gzip --keep --force elm.min.js
```

`elm-coverage` is commented out because there some compabitility issues at the time of this writing; when it works, there is no need to run `elm-test` separately.

The resulting minified file `elm.min.js.gz` is the one that should be used in production. 

## Elm Live

Note that there's no need to run the build process while developing, as Elm has good live reload tools. I use `elm-live`:

```shell
npm install -g elm-live
```

To use it to compile `src/Main.elm` and use it with `main.html`:

```shell
elm-live src/Main.elm ---optimize -open --start-page=main.html -- --output=elm.js
```

... where `main.html` can be something minimal like so:

```html
!DOCTYPE html>
<html>
  <head>
    <title>Elm App</title>
    <script src="elm.min.js.gz"></script>
    <style>
    </style>
  </head>
  <body>
    <div id="elm"></div>
    <script>
    var app = Elm.Main.init(
          { node: document.getElementById("elm"),
            flags: {
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight
            }
          }
    );
    </script>
  </body>
</html>
```

The `flags` are not necessary to provide, but it's open nice to have the window width and height for use in the Elm app.

