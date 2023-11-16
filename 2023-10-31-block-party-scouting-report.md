# How to Build a Better Robot
This paper started as a critique on the performance of a team at a robot competition. That paper was too negative to pass along, so this is an attempt to turn around and offer ways that the robot can be improved. Of course it is based on the current game, Power Up, but the suggestions should be general enough to apply to any game.

First off, let me say that I am still learning robotics, so there are a lot of things that I have missed.

If you think FRC 4513 is the best and that somehow the contest was unfair and you were robbed of your rightful place, please stop reading now. This is offered as a reflection of the event in order to improve in the future events.
## Cycle Time
My big take away from the event was "cycle time." That is the time it takes to get a game piece, travel across the field, line up and place the piece and return across the field ready to get another game piece. This varied widely between teams. 2910 and 360 were on the low end. Sometimes it was as low as 12 seconds, but in my loose way of measuring this, and never over 20 seconds. To do this they had to be both fast and quick. Fast is how I would describe the movement of the robot across the field, how much time it takes to cross the field and is mostly a mechanical measure of the robot. Quickness has to do with how much time robot uses to react to events or changes: leaving the charge station, bumping into an opponent, avoiding a alliance partner by selecting open lanes, dropping off a game piece, balancing on the charge station, opting to score another point rather than risk alliance failure on the charge station.

I timed some robots taking 45 seconds for a cycle. There were probably robots that took longer, but from a spectator point of view, these slow scoring robots were really not worth focusing on, because they were ineffectual. Think about this a little. The top robots score three times for every score they made. Or they would only be able to score three times in a match, and would not have time to engage on the charging station. Would YOU want them in your alliance?  They wasted lots of time. Taking too much time to cross the field. Waiting for confirmation that a game piece had been loaded. Waiting three seconds to know if a game piece dropped scored or not. You can't speed up gravity and you can't change the outcome. If you "need" to know, the coach could tell you, but really the driver and coach should remain focused on the next score, not worrying about a past scoring attempt that they can't do anything about.

What to do about this? As a general statement, if a robot cannot score with a low cycle time, it will not be a contender. Cycle time has to do with two things: speed and quickness.

### Speed
Most of speed comes from two factors: the force that can be supplied by a power train and the mass of the robot. In basic physics this is expressed as: 
$$
F = ma
$$
.  Focusing on just acceleration, this gets rewritten as: 
$$
a = F/m.
$$
What this means is a more powerful drive chain can produce faster acceleration (with the properly selected gear ratio). It also means that more mass will slow acceleration.

Some teams add mass just to be better ramming robots or to correct top heaviness. This results in a slower robot overall.

The fastest robots have less mass and a low center of gravity. The low
center of gravity makes the robot less likely to tip so that it is more agile in making tight turns at high speed and quick accelerations and decelerations without wobbling.

A team with a slow robot could reduce is mass by losing heavy tower and arm mechanisms and opting for a much lower and lighter profile. The robot will have reduced function, but it should be able to do what it can faster and better. As much as VIKotics is despised by the team, they move very fast around the field and also seem to be quick. Without a tower or much of an arm, they are able to score cubes on any level. They avoid cones except when on the floor. Their speed and quickness makes them a higher scorer than 4513 and tht makes them a better alliance partner.
### Quickness
Quickness is the time it takes to make changes due to circumstances: from dropping a game piece to score to the moving to get another game piece, from contact to recovery, from a problem to a new role like defense. Most of this is human reaction and decision time, but it can be reduced to near zero with practice. Some of it is mechanical like the recovery time for a wobbly top-heavy robot. This can be reduced or eliminated by avoiding the problemmatic maneuvers by practice or by the addition of sofware controls.

Quickness comes through practice. Drill on the same thing over and over until it becomes automatic and thoughtless. You don't have to drill on a full field. Drill on station pickup, floor pickup, defensive bump and run, offensive bump and run, offensive avoidance, scoring, scoring, scoring. Yes, this seems redundant and boring. Just ask yourself and your teammates, how bad you want to win or do you just want to play around.
### Avoiding Contact
If you want to be fast and have a short cycle time, avoid contact. This doesn't mean avoid contact at all costs. 2910 was effective at a bump and run defense which would disrupt the other alliance, while carrying on its primary mission of scoring with a low cycle time.

The takeaway is that if you must contact, make the contact as short of a time as possible. Don't get blocked in.
### Drive Defensively
Just like when you drive a car, anticipate what the other robots are doing so that you don't get blocked in or so that you avoid them blocking you. This needs to be communicated between driver and coach.
### Lane Selection
Good teams establish lanes with their alliance partners so that they can move back and forth and not interfere with each other. This was most important in the congested areas of the scoring grid and the substations. Rather than wait around to gain access they had open lanes for entering and leaving these areas. Sometimes the lanes were dynamic when an alliance member or opponent would block the desired lane, an alternate lane would be chosen by the coach and driver to minimize travel time.
### Automation
Certain things like pickup from ground, pickup from station or placing a game piece can be somewhat automated with the addition of vision processing software. A simple sensor may be just to tell the robot that a piece has been loaded or unloaded. This sensor can be used to end one process and begin another to give the robot some inhuman quickness.
### Efficiency
Besides staying in lanes and avoiding contact, avoid unnecessary running of motors to keep the voltage higher so that the drive chain has more power available for movement. 360 had a lot of wasted movement in its turret and twisting of its swerve based chassis. A pneumatic compressor such as on 2910 must run all the time, placing a load on the battery.
## Reliability
The reliability of a robot can be measured by the number of minutes or number of matches missed. This measure should include the type of breakdowns:
* something in the intake or delivery system, robot still able to perform in defensive roles.
* something it the robot sensors.
* something in the drive chain rendering the robot immobile.
* lost communication so nothing can be done including trouble shooting.
* a disqualification resulting in removing power from robot.
* a communication breakdown in the drive team.

Software can help with reliability. A stalled motor can be detected and then fed less power to decrease the probability of burnout. In the case of 9993, it was desirable to maintain enough power to hold a game piece, but not enough to burn out the motor. Software interventions should be visible to the technician and to the pit crew so that they can make modifications that they deem necessary.

### Simplicity Counts
Murphy's Law states that if anything can go wrong, it will. Simplicity eliminates the number of things that can go wrong, thereby improving reliability (for all things equal).

Avoiding complexity has another benefit. It allows the team to focus and refine the capabilities its robot has. Doing a few things very well is much better than trying to do a lot of things and being mediocre or worse in all of them.
### Mechanically Soundness
Mechanical soundness refers to how well mechanical connections are made. Can parts shake loose? Murphy says they will. What is lost if something shakes loose? Try to minimine the effect of any failure. As a general rule, if it doesn't look right or feel right, it probably isn't right.
### Electrically Soundness
A robot may be properly wired but connections are lost during a match. This is usually due to some force being applied where it should not be and catching a wire to force a connection apart. In general wiring should be tightly bundled so that it is mechanically stable and that nothing can catch a loose wire. Likewise conductors should be routed so that they are not subject to any rubbing or grinding contact.
## Defense
* Brings good teams down so they operate on your terms
* increases contact which may increase breakdowns and the probability of a disqualification.
* can be simply a bump and run... just slow down a competitor or force a robot out of its lane.
* should never interfere with an alliance member
## Human Element
In the robot competitions, the human team members have roles that are as important or even more important that the robot engineering. These roles are discussed below.
### Pilot
The main thing the pilot is concerned about is moving the robot and decreasing any lag time. Defensive driving should be on mind to avoid disruptions and well as possible defensive moves to disrupt opponents. Smooth driving is preferable to jerky driving to reduce shock and vibration to the robot. Speed and quickness of the driving is all important to reduce cycle time. Being out of control or reckless is harmful to the robot and its performance.
### Co-Pilot
The main concern of the co-pilot is to control the scoring features of a robot like the elevator, arm and intake device. The co-pilot should also be aware of the height of center of gravity and work to keep it as low as possible during the match.
### Coach
The coach is the eyes of the team. The coach has to decide what piece to score next in cooperation with the other teams on the alliance and to help keep the robot in a lane to avoid conflicting with alliance partners.

The coach is aware of the score, the ranking points scored and of the time remaining and the ability of the robot to perform as these aspects will control which activity the robot should do next (defense, attempt to score, or engage with the docking station).

### Human Player
The job of the human player is to deliver game pieces to a robot in a manner that does not slow down the robot. Pieces have to be ready and presented in a way desirable to the robot. Bobbles by the human player add seconds to the cycle time.
### Scouting
Train the scouts on our own robot by attending practice sessions and critiquing the robot and drive team performance. Find faults with it or the way it is driven so these things can be corrected. Find areas where the robot can be improved. (sloppy driving, human mishandling of game pieces, missing of game piece pickup or delivery, maneuvers that make the robot tippy.) Remember that these observations are not personal, but are intended to improve the performance of the team and the robot.

Measure the cycle time with a stop watch capable of doing splits. This is the fastest way to separate the great robots from the good robots. Even on a shortened practice field this measurement provides a baseline that should be beaten.
### Technician and Pit Crew 
The technician on the field should watch the robot for any problems that will need to be corrected in the pit. The technician may also observe opportunities for improving the robot in the pits or when at home.
## Desire to Improve
Even if your first attempt is good, for competition, it is not good enough. It can ALWAYS be made better.

## Fairness of the Competition
FIRST tries to make sure that the contest is a level playing field by regulating size, weight, battery and types of motors. But it cannot regulate the experience, training and desires of the teams and their mentors. It also does not regulate how much time a team may spend on their robots in the off season, build season or competition season. This time can be used to refine designs and to practice until every contingency is automatic through muscle memory. So some teams have better access to fabrication technology than others teams. Some teams have more mentors with a wider variety of experience and expertise. That may make it harder to be one of the best teams, but it certainly does not prevent you from being the best team you are capable of becoming.