+++
title = "Fixing the XAnalogTV Screensaver"
date = "2012-09-10"
aliases = ["tech-articles/fixing-the-xanalogtv-screensaver"]
tags = ["C", "technical article"]
categories = ["Technical Articles"]
banner = "img/xanalogtv_cutoff.jpg"
+++


A few days ago, I discovered the awesome XAnalogTV screensaver included with XScreenSaver. I was very impressed with the visuals, which include a very accurate simulation of a conventional “tube” television implementing the analog NTSC TV standard. There was just one problem – I couldn’t get XAnalogTV to fill my screen:

<div style="background:#eee;padding:1em;margin:1em 10%;border:1px solid #ccc;"><center>
<img src="/img/xanalogtv_cutoff.jpg" alt="XAnalogTV with Incorrect Scaling" width="70%"/>
<div class="text-small" style="padding-top:1em;">
In the source code, the virtual "display" is forced to be within 15% of a standard 4:3 display. Any screen which is outside of this 15% range is just clipped, as shown in this image.
</div></center></div>

--------

Post last updated January 15, 2013, and moved to new location on September 28, 2017.
