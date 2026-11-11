+++
title = "Software Minimalism"
date = "2026-11-10"
tags = ["minimalism", "dvr-scan", "pyscenedetect"]
categories = ["Articles"]
[cover]
image = "/img/software-minimalism.jpg"
+++

For my long-lived open source projects, I really do strive for:

 - minimal dependencies
 - simple interface
 - things should work cross platform (at minimum Linux, Windows, and macOS)
 - batteries should always be included
 - no unnecessary size bloat

Shipping software is easier if you're your own customer, or you care about a single platform. It gets much harder when you have to meet "the bar" for *other people* on arbitrary machines and operating systems.

Some of my projects have been out for over a *decade* now, with millions of downloads and widespread usage in industry and research. In that time, each project has also grown quite a lot of features. I'm grateful to all the folks who provided feedback and submitted bug reports/feature requests. Such a growing feature list creates a lot of friction usually with the above five principles.

There are always so many challenges, big and small, that can make it really difficult to adhere to these principles.  I want to share my approach for managing them over the past few years in a series of short articles.  Each challenges was difficult, some more than others, but they are all unique, and my hope is that others can learn from the experience.

This came to mind because I just released [DVR-Scan v2.0](https://www.dvr-scan.com/changelog/), one of the biggest releases yet, and it's made me think back about what it took to get here.  A new release of [PySceneDetect](https://www.scenedetect.com) was also cut this weekend, which has a ton of bug fixes and has seen a lot of contributions recently. It's cool to see how these projects getting used for both research and industry. And as always, they will remain free, open source, and most importantly, hackable.
