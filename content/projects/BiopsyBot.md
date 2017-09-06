+++
title = "Biopsy Bot"
id = "biopsybot-projectpage"
categories = ["Projects"]
type = "posts"
+++

<img src="/img/projects/biopsybot/header.jpg" alt="Biopsy Bot in Action" width="100%" />

## General Overview

A remote-control robot capable of gathering a biological sample in unknown areas, Biopsy Bot was developed as a final project for the 4th year Mechatronic System Design course offered at UWO. The purpose of the project was to develop a robot capable of remotely navigating (with the aid of an on-board wireless camera) an area of unknown, rocky terrain, in order to gather and return a biological sample from a mysterious blob (made of Jello). Furthermore, the robot is required to overcome several obstacles, while having a limited size.

Below is a short video showing off some of the construction, and the results from the final competition (the first run starts at 0:45 in):

<center><br />
<iframe src="https://www.youtube.com/embed/8z4u3RBaM9Q" width="610" height="343" frameborder="0">
</iframe> 
</center>

-------------------------------------------------------------------------------

## Technical Specifications

### Body and Drivetrain

The majority of Biopsy Bot is constructed from plexi-glass, with an aluminum-based body extension at the front. This was done to extend the length of the tracks while providing an adjustable angle for Biopsy Bot to approach the tallest obstacle with. The aluminum body extension also holds the sample gathering arm and associated motors.

There are four drive motors in total on Biopsy Bot (two per tread), and all are geared DC motors. The maximum current draw is 1.24A at 12V, again over the tallest obstacle. The treads were made using a VEX Robotics’ Tank Tread Kit, with some all-purpose silicone to improve the tread grip. There is a separate 9V power supply dedicated to the communications & control equipment, to avoid feedback and voltage sags from the motors’ power rail.

### Communications and Control

In order to use Wi-Fi as the wireless communication method, a Roving Networks RN-XV was attached to a (required) PIC24HJ64GP502 via UART. The RN-XV’s job is to forward any received TCP/UDP packets as ASCII characters to the PIC microcontroller. For this reason, a token-based communication method was used, where the microcontroller parsed the incoming data like a finite state machine, applying the appropriate signals to the relevant motors/lights on Biopsy Bot. In a loss-of-communication event, the robot is designed to stop moving within 200 milliseconds.

On the computer side, I wrote a fairly simple UDP application using the [SDL](http://www.libsdl.org/) and [SDL_net](http://www.libsdl.org/projects/SDL_net/) libraries. SDL was used to obtain the input from a generic joystick device (a PS3 controller, in this case), parse the relevant analog/digital inputs into control signals, and forward the appropriate control signals to Biopsy Bot.

### Biological Sample Collector Mechanism Design

In order to collect a sample of the mysterious blob (Jello), a syringe was attached to the motors in an old scanner head, creating the sample collection mechanism. Using a geared motor and the respective track, one side of the syringe plunger was ground down, and the track was fixed to it. A custom mounting bracket was then created out of plexi-glass, allowing the geared motor to press and retract the syringe.

Once complete, the entire mechanism was attached to a motor, so it could be raised/lowered by the robot. Part of the project requirements was to automate the sample collection process, so the automatic functionality was integrated into the control software, and could be activated by simply holding a button on the controller for a few seconds:

<center><br />
<iframe src="https://www.youtube.com/embed/u5LrPZ8Q6iQ" width="610" height="343" frameborder="0">
</iframe> 
</center>

-------------------------------------------------------------------------------

## The Team

This was a group project, with the team involving me (Brandon Castellano), Daren Michener, Ryan Mantha, and Brock Turner. Here’s a picture of us hard at work on the software, in a lab room we probably spent far too much time in together (from left-to-right is Brock, Ryan, and Daren):

<center><img src="/img/projects/biopsybot/team.jpg" alt="Biopsy Bot in Action" width="90%" /></center>
<br />

Overall the project was very successful, achieving all of the requirements set by the task, and was one of the highest ranking competetors in field testing.  Although challenging at times, it was a very fun project to work on, and I had a great time working with the team.  Lastly, thanks again to Darren, Brock, and Ryan, for all their ingenuity, hard work, and dedication in helping make Biopsy Bot.

