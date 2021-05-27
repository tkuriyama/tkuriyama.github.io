---
layout: post
title:  "Apache Rewrite Rules for Elm SPA"
date:   2021-05-27 13:00:00 -0500
tags:   elm
---

I know almost nothing about configuring and managing servers, so it took me a while to figure out how to set up an Elm single-page-application (SPA) on an Apache server.

An Elm SPA is an application that performs client-side routing from a single page (e.g. `index.html`). I set mine up manually as a learning process by referencing Richard Feldman's [canonical example](https://github.com/rtfeldman/elm-spa-example), but [elm-spa](https://package.elm-lang.org/packages/ryannhg/elm-spa/latest/) is probably the de facto tool nowadays to handle the boilerplate wiring.

Long story short, after scanning the Apache docs and this [Digital Ocean page](https://www.digitalocean.com/community/tutorials/how-to-set-up-mod_rewrite) (though I don't use Digital Ocean for hosting), the following formulation worked for my use case: redirect all URLs to `index.html` **without changing the URL string**. It's important not to change the URL (hence `Rewrite` instead of `Redirect`, as the Elm SPA parses the URL string for client-side routing.

```apacheconf
RewriteEngine on
RewriteRule ^(index.html)($|/) - [L]
RewriteRule [A-Za-z/]+ /index.html
```

The first rule prevents infinite recursion (which the server will interrupt with an error message).

I have the above in my `.htaccess` file at the public site root, but there may be a more efficient way to configure it (the internet says avoid `.htaccess` files if possible, but I'll leave that for another day).

