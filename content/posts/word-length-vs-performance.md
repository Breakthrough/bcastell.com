+++
title = "How does word length affect the performance and operation of a CPU?"
date = "2012-10-17"
aliases = ["tech-articles/how-does-word-length-affect-the-performance-and-operation-of-a-cpu"]
tags = ["technical article", "hardware"]
categories = ["Technical Articles"]
banner = "img/wordlen2.jpg"
+++


About a year ago, I came across a question on Super User titled “How much faster is a 64-bit CPU than a 32-bit CPU?”, which was promptly closed and deleted since it’s a very open ended question. However, the author (a software developer) referred to benchmarks regarding system performance in 32-bit versus 64-bit. The purpose of this blog post is to investigate how the performance of a computer is affected, as a function of the word length.

<div style="padding:0.75em;margin:1em 4em;"><center>
<img width="100%" src="/img/wordlen2.jpg" alt="Two Microcontrollers (8-bit Atmel), A Raspberry Pi (32-bit ARM), and my laptop (64-bit Intel)"/>
</center></div>

8-bit, 32-bit, and 64-bit all refer to the [word length](http://en.wikipedia.org/wiki/Word_%28computer_architecture%29) of the processor, which can be thought of as the “fundamental data type”. Often, this is the number of bits transferred to/from the RAM of the system, and the width of pointers (although nothing stops you from using software to access more RAM then what a single pointer can access). A word length can be any number of bits, but is usually a power of two.

Assuming a constant clock speed (as well as everything else in the architecture being constant), and assuming memory reads/writes are the same speed (we assume 1 clock cycle here, but this is far from the case in real life), there is no direct speed advantage from a 32-bit to a 64-bit processor, except when using higher-precision values, or lots of memory reads/writes are required. For example, if I need to add two 64-bit numbers, I can do it in a single clock cycle on a 64-bit machine (three if you count fetching the numbers from RAM):

{{< highlight ca65 >}}
     ADDA [NUM1], [NUM2]
     STAA [RESULT]
{{< /highlight >}}

However, on a 32-bit machine, I need to do this in many clock cycles, since I first need to add the lower 32-bits, and then compensate for overflow, then add the upper 64-bits:

{{< highlight ca65 >}}
     ADDA [NUM1_LOWER], [NUM2_LOWER]
     STAA [RESULT_LOWER]
     CLRA          ; I'm assuming the condition flags are not modified by this.
     BRNO CMPS     ; Branch to CMPS if there was no overflow.
     ADDA #1       ; If there was overflow, compensate the value of A.
CMPS ADDA [NUM1_UPPER], [NUM2_UPPER]
     STAA [RESULT_UPPER]
{{< /highlight >}}

Going through my made-up assembly syntax, you can easily see how higher-precision operations can take an exponentially longer time on a lower word length machine. This is the real key to 64-bit and 128-bit processors: they allow us to handle larger numbers of bits in a single operation.

Likewise, if we had to make a copy of some data in memory, assuming everything else is constant, we could copy twice as many bits per cycle on a 64-bit versus 32-bit machine. This is why 64-bit versions of many image/video editing programs outperform their 32-bit counterparts.

Back to high-precision operations, even if you add the ability to a 32-bit processor to add two 64-bit numbers in a single clock cycle, *you still need more than one clock cycle* to fetch those numbers from RAM, since the word length (again) is often the fundamental size of memory operations. So, let’s assume we have two 64-bit registers (A64 and B64), and have an operation called ADDAB64 which adds A and B, and stores it in A:

{{< highlight ca65 >}}
     LDDA64 [NUM1]   ; Takes 2 clock cycles, since this number is fetched 32-bits at a time
     LDAB64 [NUM2]   ; Again, two more clock cycles.
     ADDAB64         ; This only takes 1.
     STAA64 [RESULT] ; However, this takes two again, since we need to store a 64-bit result 32-bits at a time.
{{< /highlight >}}

As you can see, even a hardware implementation of a 64-bit addition under a 32-bit processor still takes 7 clock cycles at minimum (and this assumes all memory reads/writes take a single clock cycle). Where I’m going with this has performance implications specifically with pointers.

On a 32-bit machine, pointers can address ~4GB of RAM, where they can address over 16.7 million TB on a 64-bit machine. If you needed to address past 4GB on 32-bit, you would need to compensate for that kind of like how we added a 64-bit number on our 32-bit machine above. You would have many extra clock cycles dedicated to fetching and parsing those wider numbers, whereas those operations go much quicker on a processor that can handle it all in one word.

Also, while increasing the number of bits in an [arithmetic and logic unit (ALU)](http://en.wikipedia.org/wiki/Arithmetic_logic_unit) will increase propagation delays for most operations, this delay is very manageable in today’s processors (or else we couldn’t keep the same clock speeds as our 32-bit processor variants), and is not much use when discussing digital synchronous circuits (since everything is clocked together, if the propagation delay was too long, the processor would just crash – which is also why there are limits to overclocking).

--------

**The bottom line**: larger word lengths means we can process more data faster in the processor, which is greatly needed as we advance computing technology. This is why so many instruction set extensions (MMX, SSE, etc…) have been created: to process larger amounts of data in less amount of time.

A larger word length in a processor does not directly increase the performance of the system, but when dealing with larger (or higher precision) values is required, exponential performance gains can be realized. While the average consumer may not notice these increases, they are greatly appreciated in the fields of numeric computing, scientific analysis, video encoding, and encryption/compression.
