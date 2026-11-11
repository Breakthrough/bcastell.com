+++
title = "Fixing the XAnalogTV Screensaver"
date = "2012-09-10"
aliases = ["/tech-articles/fixing-the-xanalogtv-screensaver", "/posts/tech-articles/fixing-the-xanalogtv-screensaver"]
tags = ["C", "technical article"]
categories = ["Articles"]
[cover]
image = "/img/xanalogtv_cutoff.jpg"
+++

A few days ago, I discovered the awesome XAnalogTV screensaver included with [XScreenSaver](https://www.jwz.org/xscreensaver/). I was very impressed with the visuals, which include a very accurate simulation of a [conventional "tube" television](https://en.wikipedia.org/wiki/Cathode_ray_tube) implementing the [analog NTSC TV standard](https://en.wikipedia.org/wiki/NTSC). There was just one problem - [I couldn't get XAnalogTV to fill my screen](https://superuser.com/questions/471300/how-can-i-make-the-xanalogtv-xscreensaver-fill-my-screen).

In the above screenshot, pay attention to the edges of the screen. For some reason, the way the scaling/clipping was implemented caused the clipped portions on the screen's edges to simply not be drawn (as they should be drawn or cleared to pure black). This causes the screensaver to look quite odd, especially when there's perfectly drawn digital graphics being rendered behind the wonderful analog "snow". I found this only happens when the aspect ratio of the XAnalogTV window was very different than 4:3. Thus, in my quest for beautifully simulated analog graphics, I set out to fix this error.

I set out to download the source code from [Jamie Zawinski's website](https://www.jwz.org/xscreensaver/download.html), but at the time I wrote the post, the file he uploaded was corrupted (it has since been fixed). My next stop to find the source code lead me to the [Ubuntu Package Repository](http://packages.ubuntu.com/precise/xscreensaver), where I was able to download the source code (`xscreensaver_5.15.orig.tar.gz`). If you have a different Linux distribution, you should be able to get the source code from the distribution repository's website.

After extracting the source code, I went into the source directory, and called `./configure`. After it figured out I was missing a bunch of packages, I got all of the build dependencies via `apt`, and re-ran `./configure` successfully:

```bash
sudo apt-get build-dep xscreensaver
./configure
```

Now, it was time to start analyzing the source code. I figured the best area to start looking at would be the code that gets executed when the screen is resized from `xanalogtv.c`:

```c
static void
xanalogtv_reshape (Display *dpy,   Window window, void *closure,
                   unsigned int w, unsigned int h)
{
    struct state *st = (struct state *) closure;
    analogtv_reconfigure(st->tv);
}
```

So, XAnalogTV uses helper functions embedded in another file, `analogtv.c`. Looking at the `analogtv_reconfigure()` function, all it does is pass an object to the `analogtv_configure()` function. There, I found the following code near the beginning of the function (comments removed):

```c
    float percent = 0.15;  /* jwz: 20% caused severe top/bottom clipping
                                   in Pong on 1680x1050 iMac screen.    */
    float min_ratio = 4.0 / 3.0 * (1 - percent);
    float max_ratio = 4.0 / 3.0 * (1 + percent);
    float ratio;
    float height_snap=0.025;

    hlim = it->xgwa.height;
    wlim = it->xgwa.width;
    ratio = wlim / (float) hlim;

    if (wlim < 266 || hlim < 200)
    {
        wlim = 266;
        hlim = 200;
# ifdef DEBUG
        fprintf (stderr,
                 "size: minimal: %dx%d in %dx%d (%.3f < %.3f < %.3f)\n",
                 wlim, hlim, it->xgwa.width, it->xgwa.height,
                 min_ratio, ratio, max_ratio);
# endif
    }
    else if (ratio > min_ratio && ratio < max_ratio)
    {
# ifdef DEBUG
        fprintf (stderr,
                 "size: close enough: %dx%d (%.3f < %.3f < %.3f)\n",
                 wlim, hlim, min_ratio, ratio, max_ratio);
# endif
    }
    else if (ratio > max_ratio)
    {
        wlim = hlim*max_ratio;
# ifdef DEBUG
        fprintf (stderr,
                 "size: center H: %dx%d in %dx%d (%.3f < %.3f < %.3f)\n",
                 wlim, hlim, it->xgwa.width, it->xgwa.height,
                 min_ratio, ratio, max_ratio);
# endif
    }
    else /* ratio < min_ratio */
    {
        hlim = wlim/min_ratio;
# ifdef DEBUG
        fprintf (stderr,
                 "size: center V: %dx%d in %dx%d (%.3f < %.3f < %.3f)\n",
                 wlim, hlim, it->xgwa.width, it->xgwa.height,
                 min_ratio, ratio, max_ratio);
# endif
    }
```

From the above code, you can see that the author has constrained the displayed picture's aspect ratio to be within +/- 15% of a typical 4:3 NTSC TV. This is fine, although something must be happening in the draw function to prevent the clipped parts of the screen from actually being updated/blitted.

As a temporary fix, I modified XAnalogTV to stretch to the window/screen resolution by commenting out lines 328 and 338 in `analogtv.c`, which are listed below (respectively):

```c
      wlim = hlim*max_ratio;    /* Comment these two lines out (or remove them entirely) */
      hlim = wlim/min_ratio;    /* to prevent XAnalogTV from reshaping the display.      */
```

After that, I recompiled xscreensaver using `make`. Instead of calling `make install`, however, I simply copied my newly compiled version of the XAnalogTV binary overtop of the older one (which was found in `/usr/lib/xscreensaver/xanalogtv`):

```bash
cp /usr/lib/xscreensaver/xanalogtv /usr/lib/xscreensaver/xanalogtv.bak
sudo cp ./hacks/xanalogtv /usr/lib/xscreensaver/
```

After restarting the xscreensaver daemon, the screensaver now works as expected:

<img src="/img/xanalogtv_full.jpg" alt="XAnalogTV with correct scaling" width="1200" height="750" loading="lazy" style="display: block; margin: 1.5rem auto 0.5rem;">

*After making the fix to the code, the XAnalogTV screensaver will properly stretch-to-fit any display or aspect ratio.*

--------

## Original Comments

I was able to recover the original comments from this article via [the Wayback Machine](https://web.archive.org/web/20160307233103/http://www.bcastell.com/tech-articles/fixing-the-xanalogtv-screensaver/):

> **Dan Schmidt** &middot; 2012-09-14
>
> Finally - sombody found the solution! Much thanks. However, there was no space, it's "wlim = hlim\*max_ratio;"
>
> > **Brandon Castellano** &middot; 2012-09-14
> >
> > Thank you for pointing that out, Dan. I've updated article accordingly.

> **lexi** &middot; 2012-10-21
>
> thats great, those visible borders are really annoying! i cant work out this make thing though :(
>
> > **Brandon Castellano** &middot; 2012-10-21
> >
> > Hi Lexi;
> >
> > Sounds like you might not have some of the required build dependencies. Check the output from make, and see if it says anything regarding missing libraries or header files (indicating you might need the -dev versions of some packages).
> >
> > Thanks,<br>
> > Brandon

> **Matthew R Giese** &middot; 2012-10-21
>
> I enjoyed reading the write-up, hope I can discover a lot more articles like this one. Thanks for posting.

> **harpreet** &middot; 2013-10-13
>
> Thank you so much.<br>
> That just did the job.

> **harpreet** &middot; 2013-12-26
>
> can you please also fix the<br>
> BSOD screensaver.


