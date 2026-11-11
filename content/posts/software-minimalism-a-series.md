+++
title = "software minimalism: a series"
date = "2026-11-10"
tags = ["minimalism", "dvr-scan", "pyscenedetect"]
categories = ["Updates"]
[cover]
image = "/img/software-minimalism.jpg"
+++

Shipping software is easier if you're your own customer, or you care about a single platform. It gets much harder when you have to meet "the bar" for *other people* on arbitrary machines and operating systems. For my long-lived open source projects, I really do strive for:

 - minimal dependencies
 - simple interface
 - things should work cross platform (at minimum Linux, Windows, and macOS)
 - batteries should always be included
 - no unnecessary size bloat

[DVR-Scan](https://www.dvr-scan.com) has been out for over a *decade* now, and in that time it's grown quite a lot of features. I'm grateful to all the folks who provided feedback and submitted bug reports/feature requests, but over time a growing feature list often creates friction with the above five principles. Each of these is worth talking about on its own, since managing them over the past few years comes with unique challenges.

I'll be writing a short series about each of the above topics over the next little while, since I think some of the lessons I've learned along the way are well worth sharing.

In the meantime, I just released [DVR-Scan v2.0](https://www.dvr-scan.com/changelog/) which includes a new UI which I hope you will like, and a new version of [PySceneDetect](https://www.scenedetect.com) which has a ton of bug fixes and new stuff. It's cool to see these projects also getting mentioned in both research and industry. And as always, they will remain free, open source, and most importantly, hackable.
