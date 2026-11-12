+++
title = "Software Minimalism, Part 1: Dependencies"
date = "2026-11-11"
tags = ["minimalism", "dvr-scan", "pyscenedetect"]
categories = ["Articles"]
[cover]
image = "/img/software-minimalism-part-1.jpg"
+++

I have quite a disdain for applications that depend on "too many" third party libraries just to get them working. Sometimes though, it's hard to make the call, and sometimes, the addition might be worth it in the long run. DVR-Scan's UI uses native Tkinter, because my reasoning was that it comes "out of the box"... at least for Windows/macOS CPython. There's a `python3-tk` package that's easy and small enough to install for Linux, and many systems have it by default.

That comes with tradeoffs though: a lot of things we take for granted from various UI toolkits that just work need to be rolled by hand at times. One great example of this was when someone asked if there could be a select-all feature. They wanted to clear all the inputs before adding new ones, but were forced to remove each one individually. Honestly, I felt a bit embarrassed reading it because it seems like such an obvious usability oversight in retrospect. Maybe a part of me just assumed that the widget was working or I forgot to test it, I don't know. All I know is, thanks for the feature request, and it's now in DVR-Scan.

That's why I wanted to write this though - it also means now there's logic to handle the selection stuff. This ended up being a good thing in this case, since the inputs needed their own abstraction layer that wasn't already there. So the end result does seem to be better after a cleanup. That's not the point though - the point is I could have pulled in another dependency that creates a widget that already does this (there are *numerous* wrappers for the built-in Tkinter library already), but do they really bring anything to the table other than more abstractions? For the most part, they just make the Tkinter interface easier to use, or have custom widgets.

One major usability thing I was aware of for the initial GUI release was the lack of drag-and-drop. That, I learned early on, *was* something OS specific and would require some more help. It turns out [the `tkinter.dnd` module](https://docs.python.org/3/library/tkinter.dnd.html) is for dragging and dropping between widgets, and has nothing to do with dragging a file from your computer onto the open window.

Sure, different UI toolkits have solutions for this already, but they would require a lot more binaries to run, costing tens to hundreds of megabytes. That might not sound like a lot, but it adds up quickly across millions of downloads. That's the part that people often overlook (it's just a few more MiB, the increase is inevitable, etc.). Fortunately, I was able to find an actively maintained [tkinterdnd2 library](https://pypi.org/project/tkinterdnd2/) that provides the necessary Tcl to make this work correctly under the hood. It's also quite lightweight, and means we can stay cross-platform without pulling our hair out. [`platformdirs`](https://pypi.org/project/platformdirs/) is another good example - a small, pure Python module that's kept up to date and figures out where people expect your config files to go on each OS. There's also one for screen size ([screeninfo](https://pypi.org/project/screeninfo/)), etc. Generally, if something needs OS-specific quirks that are non-trivial, it's best to find a maintained dependency. Even better if you help them out too when you hit problems or have usability issues.

The final set of dependencies for both DVR-Scan and PySceneDetect are lean and small, which I'm quite happy with. It was a learning experience, though, to realize that some things you take for granted in certain libraries or toolkits do require some care and attention when deciding if you roll your own or just keep adding dependencies. It requires some degree of patience, willingness, and perseverance, but it is possible to stop bloat.

(And as we'll see in a future post, some packages require *much* more work to stop bloat than others do.)
