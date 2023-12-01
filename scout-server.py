''' scout-server.py
this module is to act as a holding file
for the scout-server that interacts with scout-clients and produces
a report of the scouted data.

It processes match data of a robot from a json file and produces a
summary of the robot's performance in that match.

This data includes:
time for robot to move in teleop
cones scored
cubes scored
total pieces scored
raw points scored (before bonuses)
cycles completed (score-load-score or start-load-score or start-score)
cycle time: shortest, average, longest
into scoring time: shortest, average, longest
exit scoring time: shortest, average, longest
into loading time: shortest, average, longest
exit loading time: shortest, average, longest
empty transit time: shortest, average, longest
loaded transit time: shortest, average, longest
entry lane 1 count
entry lane 2 count
entry lane 3 count
cycles completed (load-score-load)... this should be redundant
cycle time: shortest, average, longest
number of defensive hits make
number of defensive hits taken
number of congestive hits involved
number of pieces picked from floor
number of pieces dropped
engaged in autonomous
engaged in teleop
engaged attempts failed
human piece bobble
penalties
robot problems ... enumerate
time inoperable

set up to process json
want a couple of methods
reset or init 
  set all vars to 0
process json string
cycle is score, load from loading zone, score
there can be broken cycles
process preamble data
  scout idenitifier
  date and time of match start 
  match number
  team being scouted
  scout position (alliance and drive station from scoring wall)

process singular events
process timed events
  start time - start of teleOp period to robot moved
    disregard if robot does just about anyting else first
  time inoperable -- inoperable to end or to moved
  look for completed cycles
    do you keep track of extending circumstances?
        dropped
        floor pickup
        defence
        congestion

        
build a test JSON.. maybe a high scoring 2910 match
'''
import json

#periods
PRE        = 0
AUTONOMOUS = 1
TELEOP     = 2
POST       = 3
periods = [
    "Pre",
    "Auto",
    "Tele",
    "Post"
]
period = PRE

REPORT_EVENTS = True

class Stat():
    def __init__(self):
        self.high = 0
        self.low = 0
        self.cumulate = 0
        self.count = 0
        self.ave = 0

    def add( self, value):
        if value > self.high:
            self.high = value
        if self.low == 0:
            self.low = value
        elif value >0 and value < self.low:
            self.low = value
        if value > 0:
            self.cumulate += value
            self.count += 1
            self.ave = self.cumulate / self.count


class MatchStat():
    def __init__( self):
        # match descriptive data
        self.scoutIs = ""
        self.scoutPosition = ""
        self.team = 0
        self.match = ""
        self.redAlliance = ""
        self.blueAlliance = ""
        self.scoutingPosition = ""
        self.team = ""
        self.scoutName = ""
        self.clockStarted = ""
        self.clockStopped = ""
        self.redScore = ""
        self.blueScore = ""
        self.redRankingPoints = ""
        self.blueRankingPoints = ""

        #match performance data
        self.autoDocked = False
        self.autoMobility = False
        self.autoEngaged = False
        self.congestion = 0
        self.completeCycles = 0
        self.defended = 0
        self.defending = 0
        self.disengaged = 0
        self.engaged = 0
        self.floorPickup = 0
        self.humanBobble = 0
        self.pieceDropped = 0
        self.piecesLoadedFromStation = 0
        self.timeInoperable = 0
        self.timeToStartAuto = 0
        self.timeToStartTeleOp = 0
        self.timeDockedTeleOp = 0

        self.scoredConeHighAuto = 0
        self.scoredConeHighTeleOp = 0
        self.scoredConeLowAuto = 0
        self.scoredConeLowTeleOp = 0
        self.scoredConeMedAuto = 0
        self.scoredConeMedTeleOp = 0
        self.scoredCubeHighAuto = 0
        self.scoredCubeHighTeleOp = 0
        self.scoredCubeLowAuto = 0
        self.scoredCubeLowTeleOp = 0
        self.scoredCubeMedAuto = 0
        self.scoredCubeMedTeleOp = 0

        self.teleMobility = False
        self.teleDocked = False
        self.teleEngaged = False

        self.timeToExitScoring  = 0
        self.timeToTransitEmpty = 0
        self.timeToLoad         = 0
        self.timeToExitLoading  = 0
        self.timeToTransitFull  = 0
        self.timeToScore        = 0
        self.timeCycle          = 0

        self.summary = {}
        self.summary[ 'timeToExitScoring']  = Stat()
        self.summary[ 'timeToTransitEmpty'] = Stat()
        self.summary[ 'timeToLoad']         = Stat()
        self.summary[ 'timeToScore']        = Stat()
        self.summary[ 'timeToExitLoading']  = Stat()
        self.summary[ 'timeToTransitFull']  = Stat()
        self.summary[ 'timeCycle']          = Stat()

        self.numEvents = 0
        self.comments = []
        self.cycles = []

    def _initCycle( self):
        self.timeToExitScoring  = 0
        self.timeToTransitEmpty = 0
        self.timeToLoad         = 0
        self.timeToExitLoading  = 0
        self.timeToTransitFull  = 0
        self.timeToScore        = 0
        self.timeCycle          = 0


    def _recordCycle( self):
        cycle = {}
        cycle[ "complete"] = True #... more testing required
        cycle[ "timeToExitScoring"]  = self.timeToExitScoring
        cycle[ "timeToTransitEmpty"] = self.timeToTransitEmpty
        cycle[ "timeToLoad"]         = self.timeToLoad
        cycle[ "timeToExitLoading"]  = self.timeToExitLoading
        cycle[ "timeToTransitFull"]  = self.timeToTransitFull
        cycle[ "timeToScore"]        = self.timeToScore
        cycle[ "timeCycle"]          = self.timeCycle
        self.cycles.append( cycle)
        self.summary[ 'timeToExitScoring'].add(  self.timeToExitScoring)
        self.summary[ 'timeToTransitEmpty'].add( self.timeToTransitEmpty)
        self.summary[ 'timeToLoad'].add(         self.timeToLoad)
        self.summary[ 'timeToScore'].add(        self.timeToScore)
        self.summary[ 'timeToExitLoading'].add(     self.timeToExitLoading)
        self.summary[ 'timeToTransitFull'].add(  self.timeToTransitFull)
        self.summary[ 'timeCycle'].add(          self.timeCycle)


    def importJSON (self, jsonString): # load up data
        #read the string
        self.struct = json.loads( JSON_STRING)
        #print(json.dumps(struct, indent=4))

        #process header and footer items
        self.match             = self.struct['match']
        self.redAlliance       = self.struct['redAlliance']
        self.blueAlliance      = self.struct['blueAlliance']
        self.scoutingPosition  = self.struct['scoutingPosition']
        self.team              = self.struct['team']
        self.scoutName         = self.struct['scoutName']
        self.clockStarted      = self.struct['clockStarted']
        self.clockStopped      = self.struct['clockStopped']
        self.redScore          = self.struct['matchScore']['redAlliance']
        self.blueScore         = self.struct['matchScore']['blueAlliance']
        self.redRankingPoints  = self.struct['rankingPoints']['redAlliance']
        self.blueRankingPoints = self.struct['rankingPoints']['blueAlliance']

        self.numEvents = len(self.struct['events'])
        self.cycles = []
        cycle = {}

        #loop through all events
        firstEvent = True
        self.inoperable = False  # assume a working robot
        #period = AUTONOMOUS     # have to assume this for now... is this used?? 
        autoStartTime = 30      # have to assume this for now
        teleOpStartTime  = 135  # have to assume this for now
        cycleStarted = teleOpStartTime  # have to assume this for now
        lastTimedEvent = "scored"
        lastTimedEventTime = teleOpStartTime
        for event in range(0, self.numEvents):
            eventPeriod = self.struct['events'][event]['period']
            eventTime = self.struct['events'][event]['time']
            eventName = self.struct['events'][event]['event']
            match eventName:
                case "Robot Moved":
                    if firstEvent:
                        if eventPeriod == "Auto":
                            self.timeToStartAuto = autoStartTime - eventTime
                        elif eventPeriod == "Tele":
                            self.timeToStartTeleOp = teleOpStartTime - eventTime
                    elif self.inoperable:
                        self.timeInoperable += inoperativeStartTime - eventTime
                        self.inoperable = False
                case "Floor Pickup":
                    self.floorPickup += 1
                case "Piece Dropped":
                    self.pieceDropped += 1
                case "Human Bobble":
                    self.humanBobble += 1
                case "Defended":
                    self.defended += 1
                case "Defending":
                    self.defending += 1
                case "Congestion":
                    self.congestion += 1
                case "Docked":
                    if eventPeriod == "Auto":
                        self.autoDocked = True
                    elif eventPeriod == "Tele":
                        self.teleDocked = True
                        if self.timeDockedTeleOp == 0:
                            self.timeDockedTeleOp = eventTime
                case "Undocked":
                    if eventPeriod == "Auto":
                        self.autoDocked = False
                    elif eventPeriod == "Tele":
                        self.teleDocked = False
                case "Engaged":
                    self.engaged += 1
                    if eventPeriod == "Auto":
                        self.autoEngaged = True
                    elif eventPeriod == "Tele":
                        self.teleEngaged = True
                case "Disengaged":
                    if eventPeriod == "Auto":
                        self.autoEngaged = False
                    elif eventPeriod == "Tele":
                        self.teleEngaged = False
                    self.disengaged += 1
                case "Inoperative":
                    if self.inoperable:
                        pass # just ignore a double reporting
                    else:
                        inoperativeStartTime = eventTime
                        self.inoperable = True

                #process event as part of a cycle
                case "Score Cube High":
                    if eventPeriod == "Auto":
                        self.scoredCubeHighAuto += 1
                    else:
                        self.scoredCubeHighTeleOp += 1
                        #end one cycle and start next
                        self.timeCycle = cycleStarted - eventTime
                        self.timeToScore = lastTimedEventTime - eventTime
                        self._recordCycle()
                        self._initCycle()
                        lastTimedEvent = "scored"
                        lastTimedEventTime = eventTime
                        cycleStarted = eventTime

                case "Score Cone High":
                    if eventPeriod == "Auto":
                        self.scoredConeHighAuto += 1
                    else:
                        self.scoredConeHighTeleOp += 1
                        #end one cycle and start next
                        self.timeCycle = cycleStarted - eventTime
                        self.timeToScore = lastTimedEventTime - eventTime
                        self._recordCycle()
                        self._initCycle()
                        lastTimedEvent = "scored"
                        lastTimedEventTime = eventTime
                        cycleStarted = eventTime

                case "Score Cube Medium":
                    if eventPeriod == "Auto":
                        self.scoredCubeMedAuto += 1
                    else:
                        self.scoredCubeMedTeleOp += 1
                        #end one cycle and start next
                        self.timeCycle = cycleStarted - eventTime
                        self.timeToScore = lastTimedEventTime - eventTime
                        self._recordCycle()
                        self._initCycle()
                        lastTimedEvent = "scored"
                        lastTimedEventTime = eventTime
                        cycleStarted = eventTime

                case "Score Cone Medium":
                    if eventPeriod == "Auto":
                        self.scoredConeMedAuto += 1
                    else:
                        self.scoredConeMedTeleOp += 1
                        #end one cycle and start next
                        self.timeCycle = cycleStarted - eventTime
                        self.timeToScore = lastTimedEventTime - eventTime
                        self._recordCycle()
                        self._initCycle()
                        lastTimedEvent = "scored"
                        lastTimedEventTime = eventTime
                        cycleStarted = eventTime

                case "Score Cube Low":
                    if eventPeriod == "Auto":
                        self.scoredCubeLowAuto += 1
                    else:
                        self.scoredCubeLowTeleOp += 1
                        #end one cycle and start next
                        self.timeCycle = cycleStarted - eventTime
                        self.timeToScore = lastTimedEventTime - eventTime
                        self._recordCycle()
                        self._initCycle()
                        lastTimedEvent = "scored"
                        lastTimedEventTime = eventTime
                        cycleStarted = eventTime

                case "Score Cone Low":
                    if eventPeriod == "Auto":
                        self.scoredConeLowAuto += 1
                    else:
                        self.scoredConeLowTeleOp += 1
                        #end one cycle and start next
                        self.timeCycle = cycleStarted - eventTime
                        self.timeToScore = lastTimedEventTime - eventTime
                        self._recordCycle()
                        self._initCycle()
                        lastTimedEvent = "scored"
                        lastTimedEventTime = eventTime
                        cycleStarted = eventTime

                case "Left Community":
                    if firstEvent:
                        if eventPeriod == "Auto":
                            self.timeToStartAuto = autoStartTime - eventTime
                        elif eventPeriod == "Tele":
                            self.timeToStartTeleOp = teleOpStartTime - eventTime
                    if eventPeriod == "Auto":
                        self.autoMobility = True
                    else:
                        if lastTimedEvent == "scored":
                            self.timeToExitScoring = lastTimedEventTime - eventTime
                        else:
                            unexpectedEvent = True
                        lastTimedEvent = "leftCommunity"
                        lastTimedEventTime = eventTime

                case "Enter Loading Area":
                    if firstEvent:
                        if eventPeriod == "Auto":
                            self.timeToStartAuto = autoStartTime - eventTime
                        elif eventPeriod == "Tele":
                            self.timeToStartTeleOp = teleOpStartTime - eventTime
                    if lastTimedEvent == "leftCommunity":
                        self.timeToTransitEmpty = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True
                    lastTimedEvent = "enterLoadingArea"
                    lastTimedEventTime = eventTime

                case "Floor Pickup":
                    self.floorPickup += 1
                    if lastTimedEvent == "enterLoadingArea":
                        self.timeToLoad = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True
                    lastTimedEvent = "pieceLoaded"
                    lastTimedEventTime = eventTime

                case "Piece Loaded":
                    self.piecesLoadedFromStation += 1
                    if lastTimedEvent == "enterLoadingArea":
                        self.timeToLoad = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True
                    lastTimedEvent = "pieceLoaded"
                    lastTimedEventTime = eventTime

                case "Left Loading Area":
                    if lastTimedEvent == "pieceLoaded":
                        self.timeToExitLoading = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True
                    lastTimedEvent = "leftLoadingArea"
                    lastTimedEventTime = eventTime

                case "Enter Community 1": # can't really do this, but for now...
                    if lastTimedEvent == "leftLoadingArea":
                        self.timeToTransitFull = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True

                    lastTimedEvent = "enterCommunity"
                    lastTimedEventTime = eventTime

                case "Enter Community 2":
                    if lastTimedEvent == "leftLoadingArea":
                        self.timeToTransitFull = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True

                    lastTimedEvent = "enterCommunity"
                    lastTimedEventTime = eventTime

                case "Enter Community 3":
                    if lastTimedEvent == "leftLoadingArea":
                        self.timeToTransitFull = lastTimedEventTime - eventTime
                    else:
                        unexpectedEvent = True

                    lastTimedEvent = "enterCommunity"
                    lastTimedEventTime = eventTime

                case _:
                    print ( f"Unhandled event: {eventName}.") # record this as part of the 

            firstEvent = False

        #write teamMatch record to database

    def _genCycleReport( self, cycleNumber, cycle):
        # print information about a cycle, removing zero values
        total = f"{cycle['timeCycle']:4.1f}"
        if total == " 0.0":
            total = "    "
        exitScoring = f"{cycle['timeToExitScoring']:4.1f}"
        if exitScoring == " 0.0":
            exitScoring = "    "
        transitEmpty = f"{cycle['timeToTransitEmpty']:4.1f}"
        if transitEmpty == " 0.0":
            transitEmpty = "    "
        loading = f"{cycle['timeToLoad']:4.1f}"
        if loading == " 0.0":
            loading = "    "
        exitLoading = f"{cycle['timeToExitLoading']:4.1f}"
        if exitLoading == " 0.0":
            exitLoading = "    "
        transitFull = f"{cycle['timeToTransitFull']:4.1f}"
        if transitFull == " 0.0":
            transitFull = "    "
        scoring = f"{cycle['timeToScore']:4.1f}"
        if scoring == " 0.0":
            scoring = "    "

        print( f"Cycle {cycleNumber}: tot:{total} exit:{exitScoring} empty:{transitEmpty} load:{loading} exit:{exitLoading} full:{transitFull} score:{scoring}")
        #print( f'Cycle {cycleNumber}:  tot:{cycle["timeCycle"]:4.1f}  exit:{cycle["timeToExitScoring"]:4.1f}  empty:{cycle["timeToTransitEmpty"]:4.1f}  load:{cycle["timeToLoad"]:4.1f}  exit:{cycle["timeToExitLoading"]:4.1f}  full:{cycle["timeToTransitFull"]:4.1f}  score:{cycle["timeToScore"]:4.1f}')
        

    def genMatchReport( self):
        print( f"Match:               {self.match}")
        print( f"Red Alliance:        {self.redAlliance}")
        print( f"Blue Alliance:       {self.blueAlliance}")
        print( f"Scouting Position:   {self.scoutingPosition}")
        print( f"Team:                {self.team}")
        print( f"Scout Name:          {self.scoutName}")
        print( f"Clock Started:       {self.clockStarted}")

        if REPORT_EVENTS:
            print ("\nAutonomous Events")
            for event in range(0, self.numEvents):
                eventPeriod = self.struct['events'][event]['period']
                if eventPeriod == "Auto":
                    eventTime = self.struct['events'][event]['time']
                    eventName = self.struct['events'][event]['event']
                    if REPORT_EVENTS:
                        print( f"{eventPeriod:5} {eventTime:5.1f} {eventName}")
            print( "")

        print("Scoring contribution autonomous")
        high = self.scoredCubeHighAuto + self.scoredConeHighAuto
        med = self.scoredCubeMedAuto + self.scoredConeMedAuto
        low = self.scoredCubeLowAuto + self.scoredConeLowAuto
        highPoints = 6 * high
        medPoints = 4 * med
        lowPoints = 3 * low
        total = high + med + low
        totalPiecePoints = highPoints + medPoints + lowPoints
        if self.autoMobility:
            mobilityPoints = 3
        else:
            mobilityPoints = 0
        if self.autoDocked:
            dockedPoints = 8
        else:
            dockedPoints = 0
        if self.autoEngaged:
            engagedPoints = 4
        else:
            engagedPoints = 0
        totalPoints = totalPiecePoints + mobilityPoints + dockedPoints + engagedPoints
        #automous max = pieces (3+4) *6 + docked* 8 engaged *4 +  mobility*3
        #= 42+12+9 = 63
        percentage = 100.0 * totalPoints / 63

        print( f"Pieces scored: high:{high}:{highPoints} med {med}:{medPoints} low:{low}:{lowPoints} total:{total}:{totalPiecePoints}")
        print( f"Mobility points: {mobilityPoints}")
        print( f"Docked points: {dockedPoints}")
        print( f"Engaged points: {engagedPoints}")
        print( f"Total {totalPoints} ({percentage:.0f}% of possible points)")
        print("")

        if REPORT_EVENTS:
            cycle = 0
            print ("\nTeleOp Events and Cycles")
            for event in range(0, self.numEvents):
                eventPeriod = self.struct['events'][event]['period']
                if eventPeriod == "Tele":
                    eventTime = self.struct['events'][event]['time']
                    eventName = self.struct['events'][event]['event']
                    if REPORT_EVENTS:
                        print( f"{eventPeriod:5} {eventTime:5.1f} {eventName}")
                    if eventName.find("Score") == 0 and cycle < len(self.cycles):
                        #print (f"cycle:{cycle}  numCycles:{len(self.cycles)}")
                        self._genCycleReport( cycle, self.cycles[cycle])
                        cycle += 1
                        print( "")
            

        # print summary date
        print( "")
        print( "Cycle Summary             count   low  high   ave")
        print( f"Time to exit scoring area: {self.summary[ 'timeToExitScoring'].count:4}  {self.summary[ 'timeToExitScoring'].low:4.1f}  {self.summary[ 'timeToExitScoring'].high:4.1f}  {self.summary[ 'timeToExitScoring'].ave:4.1f}")
        print( f"Time to transit empty:     {self.summary[ 'timeToTransitEmpty'].count:4}  {self.summary[ 'timeToTransitEmpty'].low:4.1f}  {self.summary[ 'timeToTransitEmpty'].high:4.1f}  {self.summary[ 'timeToTransitEmpty'].ave:4.1f}")
        print( f"Time to load:              {self.summary[ 'timeToLoad'].count:4}  {self.summary[ 'timeToLoad'].low:4.1f}  {self.summary[ 'timeToLoad'].high:4.1f}  {self.summary[ 'timeToLoad'].ave:4.1f}")
        print( f"Time to exit loading area: {self.summary[ 'timeToExitLoading'].count:4}  {self.summary[ 'timeToExitLoading'].low:4.1f}  {self.summary[ 'timeToExitLoading'].high:4.1f}  {self.summary[ 'timeToExitLoading'].ave:4.1f}")
        print( f"Time to transit full:      {self.summary[ 'timeToTransitFull'].count:4}  {self.summary[ 'timeToTransitFull'].low:4.1f}  {self.summary[ 'timeToTransitFull'].high:4.1f}  {self.summary[ 'timeToTransitFull'].ave:4.1f}")
        print( f"Time to score:             {self.summary[ 'timeToScore'].count:4}  {self.summary[ 'timeToScore'].low:4.1f}  {self.summary[ 'timeToScore'].high:4.1f}  {self.summary[ 'timeToScore'].ave:4.1f}")
        print( f"Time for entire cycle:     {self.summary[ 'timeToScore'].count:4}  {self.summary[ 'timeCycle'].low:4.1f}  {self.summary[ 'timeCycle'].high:4.1f}  {self.summary[ 'timeCycle'].ave:4.1f}")
        print( "")
        print( f"Time for first move:                        {self.timeToStartTeleOp:5.1f}")
        print( f"Time inoperable:                            {self.timeInoperable:5.1f}")
        print( f"Time docked:                                {self.timeDockedTeleOp:5.1f}")
        print( "")

        high = self.scoredCubeHighTeleOp + self.scoredConeHighTeleOp
        med = self.scoredCubeMedTeleOp + self.scoredConeMedTeleOp
        low = self.scoredCubeLowTeleOp + self.scoredConeLowTeleOp
        total = high + med + low
        highPoints = 5 * high
        medPoints = 3 * med
        lowPoints = 2 * low
        totalPiecePoints = highPoints + medPoints + lowPoints
        print( f"Pieces scored: high: {high}:{highPoints} med: {med}:{medPoints} low: {low}:{lowPoints} total:{total}:{totalPiecePoints}")
        totalCubes = self.scoredCubeHighTeleOp + self.scoredCubeMedTeleOp +\
                     self.scoredCubeLowTeleOp + self.scoredCubeHighAuto +\
                     self.scoredCubeMedAuto + self.scoredCubeLowAuto
        totalCones = self.scoredConeHighTeleOp + self.scoredConeMedTeleOp +\
                     self.scoredConeLowTeleOp + self.scoredConeHighAuto +\
                     self.scoredConeMedAuto + self.scoredConeLowAuto
        print( f"Scored {totalCubes} cubes and {totalCones} cones (auto and teleOp)")

        if self.teleDocked:
            dockedPoints = 6
        else:
            dockedPoints = 0
        if self.teleEngaged:
            engagedPoints = 10
        else:
            engagedPoints = 0
        print( f"Docked points: {dockedPoints}")
        print( f"Engaged points: {engagedPoints}")

        totalPoints = totalPiecePoints + dockedPoints + engagedPoints
        #teleop max = pieces 9 * (2+3+5) + docked* 3*6 engaged *3*4
        #= 90 + 28 +12 = 130 - 7*5 = 95
        percentage = 100.0 * totalPoints / 95
        print( f"Total {totalPoints} ({percentage:.0f}% of possible points)")

        print( "")
        print( f"Floor Pickup:  {self.floorPickup}")
        print( f"Piece Dropped: {self.pieceDropped}")
        print( f"Human Bobble:  {self.humanBobble}")
        print( f"Defended:      {self.defended}")
        print( f"Defending:     {self.defending}")
        print( f"Congestion:    {self.congestion}")

        print( "")
        print( f"Clock Stopped:       {self.clockStopped}")
        print( f"Red Score:           {self.redScore}")
        print( f"Blue Score:          {self.blueScore}")
        print( f"Red Ranking Points:  {self.redRankingPoints}")
        print( f"Blue Ranking Points: {self.blueRankingPoints}")

# block party match 1 4513a
#JSON_STRING='{"match":"1","redAlliance":[9999,5937,8051],"blueAlliance":[3663,5941,2930],"scoutingPosition":"red 3","team":4513,"scoutName":"Kirk","clockStarted":"2023/11/17 10:14:19.180","events":[{"period":"Auto","time":8.3,"event":"Robot Moved"},{"period":"Auto","time":7.1,"event":"Score Cube Medium"},{"period":"Auto","time":5.9,"event":"Engaged"},{"period":"Tele","time":8.8,"event":"Piece Dropped"},{"period":"Tele","time":7.5,"event":"Enter Community 1"},{"period":"Tele","time":5.9,"event":"Score Cube High"},{"period":"Tele","time":4.3,"event":"Left Community"},{"period":"Tele","time":3.3,"event":"Enter Loading Area"},{"period":"Tele","time":2.3,"event":"Piece Loaded"},{"period":"Tele","time":1.3,"event":"Enter Community 2"},{"period":"Tele","time":0.3,"event":"Score Cone High"}], "clockStopped":"2023/11/17 10:14:39.182","matchScore":{"redAlliance":22,"blueAlliance":33},"rankingPoints":{"redAlliance":1,"blueAlliance":2}}'
# block party match 1 4513b
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 3",    "team":4513,    "scoutName":"kirk",    "clockStarted":"2023/11/20 08:35:24.973",    "events":[{ "period":"Auto", "time":28.8, "event":"Robot Moved"},{ "period":"Auto", "time":27.8, "event":"Floor Pickup"},{ "period":"Auto", "time":26.6, "event":"Piece Dropped"},{ "period":"Auto", "time":25.0, "event":"Score Cube High"},{ "period":"Auto", "time":24.0, "event":"Docked"},{ "period":"Auto", "time":22.8, "event":"Engaged"},{ "period":"Auto", "time":18.4, "event":"Score Cube High"},{ "period":"Auto", "time":17.3, "event":"Score Cube Medium"},{ "period":"Auto", "time":15.2, "event":"Score Cone High"},{ "period":"Auto", "time":14.1, "event":"Score Cone Medium"},{ "period":"Auto", "time":13.2, "event":"Score Cone Low"},{ "period":"Auto", "time":10.8, "event":"Left Community"},{ "period":"Tele", "time":130.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":129.8, "event":"Piece Loaded"},{ "period":"Tele", "time":128.8, "event":"Left Loading Area"},{ "period":"Tele", "time":126.7, "event":"Score Cube High"},{ "period":"Tele", "time":122.6, "event":"Left Loading Area"},{ "period":"Tele", "time":119.3, "event":"Score Cone High"},{ "period":"Tele", "time":118.2, "event":"Left Community"},{ "period":"Tele", "time":117.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":116.0, "event":"Piece Loaded"},{ "period":"Tele", "time":114.9, "event":"Left Loading Area"},{ "period":"Tele", "time":109.7, "event":"Piece Loaded"},{ "period":"Tele", "time":108.7, "event":"Left Loading Area"},{ "period":"Tele", "time":107.5, "event":"Enter Community 1"},{ "period":"Tele", "time":106.3, "event":"Score Cube High"},{ "period":"Tele", "time":103.8, "event":"Left Community"},{ "period":"Tele", "time":102.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":100.7, "event":"Left Loading Area"},{ "period":"Tele", "time":98.0, "event":"Score Cone Low"},{ "period":"Tele", "time":97.2, "event":"Left Community"},{ "period":"Tele", "time":96.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":95.3, "event":"Piece Loaded"},{ "period":"Tele", "time":94.4, "event":"Left Loading Area"},{ "period":"Tele", "time":89.6, "event":"Score Cone Medium"},{ "period":"Tele", "time":87.4, "event":"Enter Loading Area"},{ "period":"Tele", "time":86.5, "event":"Piece Loaded"},{ "period":"Tele", "time":85.7, "event":"Left Loading Area"},{ "period":"Tele", "time":83.7, "event":"Enter Community 2"},{ "period":"Tele", "time":82.6, "event":"Score Cube Medium"},{ "period":"Tele", "time":80.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":80.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":79.3, "event":"Piece Loaded"},{ "period":"Tele", "time":78.3, "event":"Left Loading Area"},{ "period":"Tele", "time":75.3, "event":"Defending"},{ "period":"Tele", "time":73.4, "event":"Congestion"},{ "period":"Tele", "time":71.4, "event":"Docked"},{ "period":"Tele", "time":70.0, "event":"Undocked"},{ "period":"Tele", "time":69.2, "event":"Engaged"},{ "period":"Tele", "time":67.0, "event":"Disengaged"},{ "period":"Tele", "time":62.5, "event":"robot pickup malfunction"},{ "period":"Tele", "time":60.2, "event":"Robot Moved"},{ "period":"Tele", "time":59.0, "event":"Floor Pickup"},{ "period":"Tele", "time":58.0, "event":"Piece Dropped"},{ "period":"Tele", "time":56.0, "event":"Human Bobble"},{ "period":"Tele", "time":54.5, "event":"Enter Community 1"},{ "period":"Tele", "time":53.6, "event":"Score Cube High"},{ "period":"Tele", "time":50.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":49.0, "event":"Piece Loaded"},{ "period":"Tele", "time":48.1, "event":"Left Loading Area"},{ "period":"Tele", "time":46.0, "event":"Enter Community 2"},{ "period":"Tele", "time":44.7, "event":"Score Cone High"},{ "period":"Tele", "time":43.1, "event":"Left Community"},{ "period":"Tele", "time":42.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":41.0, "event":"Piece Loaded"},{ "period":"Tele", "time":40.1, "event":"Piece Loaded"},{ "period":"Tele", "time":37.9, "event":"Enter Community 1"},{ "period":"Tele", "time":36.8, "event":"Score Cube High"},{ "period":"Tele", "time":35.7, "event":"Left Community"},{ "period":"Tele", "time":33.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":31.5, "event":"Piece Loaded"},{ "period":"Tele", "time":30.6, "event":"Left Loading Area"},{ "period":"Tele", "time":29.2, "event":"Enter Community 1"},{ "period":"Tele", "time":26.5, "event":"Score Cube High"},{ "period":"Tele", "time":23.6, "event":"Enter Loading Area"},{ "period":"Tele", "time":22.5, "event":"Piece Loaded"},{ "period":"Tele", "time":21.4, "event":"Left Loading Area"},{ "period":"Tele", "time":19.3, "event":"Enter Community 2"},{ "period":"Tele", "time":18.3, "event":"Score Cone High"},{ "period":"Tele", "time":15.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":14.0, "event":"Piece Loaded"},{ "period":"Tele", "time":12.3, "event":"Left Loading Area"},{ "period":"Tele", "time":7.3, "event":"Docked"},{ "period":"Tele", "time":6.1, "event":"Engaged"}],    "clockStopped":"2023/11/20 08:38:09.973",    "matchScore": {        "redAlliance":23,        "blueAlliance":32    },    "rankingPoints": {        "redAlliance":1,        "blueAlliance":4    }}'
# PNCMP qual 82 2910  81a
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 1",    "team":6350,    "scoutName":"",    "clockStarted":"2023/11/21 08:27:36.132",    "events":[{ "period":"Auto", "time":28.9, "event":"Robot Moved"},{ "period":"Auto", "time":28.7, "event":"Robot Moved"},{ "period":"Auto", "time":27.7, "event":"Score Cube High"},{ "period":"Auto", "time":24.3, "event":"Floor Pickup"},{ "period":"Auto", "time":23.3, "event":"Score Cube High"},{ "period":"Auto", "time":19.9, "event":"Piece Dropped"},{ "period":"Auto", "time":16.7, "event":"Score Cube Medium"},{ "period":"Auto", "time":0.9, "event":"Score Cube High"},{ "period":"Tele", "time":131.9, "event":"Enter Community 1"},{ "period":"Tele", "time":130.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":123.4, "event":"Enter Loading Area"},{ "period":"Tele", "time":123.0, "event":"Piece Loaded"},{ "period":"Tele", "time":118.8, "event":"Enter Community 2"},{ "period":"Tele", "time":116.8, "event":"Score Cube High"},{ "period":"Tele", "time":112.6, "event":"Left Community"},{ "period":"Tele", "time":111.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":110.0, "event":"Piece Loaded"},{ "period":"Tele", "time":109.3, "event":"Left Loading Area"},{ "period":"Tele", "time":107.3, "event":"Enter Community 1"},{ "period":"Tele", "time":105.2, "event":"Score Cube High"},{ "period":"Tele", "time":99.3, "event":"Left Community"},{ "period":"Tele", "time":98.7, "event":"Piece Loaded"},{ "period":"Tele", "time":97.0, "event":"Piece Loaded"},{ "period":"Tele", "time":96.0, "event":"Left Loading Area"},{ "period":"Tele", "time":90.2, "event":"Enter Community 1"},{ "period":"Tele", "time":87.2, "event":"Score Cone High"},{ "period":"Tele", "time":84.2, "event":"Left Community"},{ "period":"Tele", "time":82.5, "event":"Enter Loading Area"},{ "period":"Tele", "time":80.3, "event":"Piece Loaded"},{ "period":"Tele", "time":79.5, "event":"Left Loading Area"},{ "period":"Tele", "time":72.8, "event":"Score Cone High"},{ "period":"Tele", "time":69.8, "event":"Left Community"},{ "period":"Tele", "time":65.0, "event":"Enter Loading Area"},{ "period":"Tele", "time":63.4, "event":"Piece Loaded"},{ "period":"Tele", "time":56.4, "event":"Score Cone Low"},{ "period":"Tele", "time":48.1, "event":"Enter Community 1"},{ "period":"Tele", "time":43.3, "event":"Score Cube Low"},{ "period":"Tele", "time":42.5, "event":"Left Community"},{ "period":"Tele", "time":41.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":40.2, "event":"Piece Loaded"},{ "period":"Tele", "time":36.3, "event":"Robot Moved"},{ "period":"Tele", "time":35.0, "event":"Floor Pickup"},{ "period":"Tele", "time":29.7, "event":"Score Cube Low"},{ "period":"Tele", "time":28.6, "event":"Left Community"},{ "period":"Tele", "time":25.4, "event":"Piece Loaded"},{ "period":"Tele", "time":22.3, "event":"Enter Community 1"},{ "period":"Tele", "time":15.6, "event":"Docked"},{ "period":"Tele", "time":13.1, "event":"Engaged"}],    "clockStopped":"2023/11/21 08:30:21.137",    "matchScore": {        "redAlliance":0,        "blueAlliance":0    },    "rankingPoints": {        "redAlliance":0,        "blueAlliance":0    }}'
#2910 Champ match 82b
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 1",    "team":2910,    "scoutName":"Kirk pncmp 82",    "clockStarted":"2023/11/21 08:45:58.699",    "events":[{ "period":"Auto", "time":28.7, "event":"Robot Moved"},{ "period":"Auto", "time":28.1, "event":"Score Cube High"},{ "period":"Auto", "time":19.5, "event":"Piece Loaded"},{ "period":"Auto", "time":18.8, "event":"Score Cube High"},{ "period":"Auto", "time":13.5, "event":"Piece Loaded"},{ "period":"Auto", "time":11.1, "event":"Score Cube Medium"},{ "period":"Tele", "time":134.3, "event":"Left Community"},{ "period":"Tele", "time":132.9, "event":"Piece Loaded"},{ "period":"Tele", "time":127.8, "event":"Score Cube High"},{ "period":"Tele", "time":126.8, "event":"Left Community"},{ "period":"Tele", "time":125.0, "event":"Enter Loading Area"},{ "period":"Tele", "time":119.5, "event":"Piece Loaded"},{ "period":"Tele", "time":118.9, "event":"Left Loading Area"},{ "period":"Tele", "time":115.5, "event":"Enter Community 2"},{ "period":"Tele", "time":111.4, "event":"Score Cone High"},{ "period":"Tele", "time":110.1, "event":"Left Community"},{ "period":"Tele", "time":107.9, "event":"Piece Loaded"},{ "period":"Tele", "time":107.1, "event":"Piece Loaded"},{ "period":"Tele", "time":103.3, "event":"Enter Community 1"},{ "period":"Tele", "time":100.4, "event":"Score Cube Medium"},{ "period":"Tele", "time":97.9, "event":"Left Community"},{ "period":"Tele", "time":94.3, "event":"Piece Loaded"},{ "period":"Tele", "time":92.7, "event":"Piece Loaded"},{ "period":"Tele", "time":90.6, "event":"Left Loading Area"},{ "period":"Tele", "time":85.3, "event":"Enter Community 1"},{ "period":"Tele", "time":82.4, "event":"Left Community"},{ "period":"Tele", "time":47.1, "event":"Piece Loaded"},{ "period":"Tele", "time":46.5, "event":"Piece Loaded"},{ "period":"Tele", "time":45.9, "event":"Left Loading Area"},{ "period":"Tele", "time":43.6, "event":"Enter Community 1"},{ "period":"Tele", "time":40.2, "event":"Score Cube Low"},{ "period":"Tele", "time":39.0, "event":"Left Community"},{ "period":"Tele", "time":36.6, "event":"Enter Loading Area"},{ "period":"Tele", "time":34.3, "event":"Piece Loaded"},{ "period":"Tele", "time":32.0, "event":"Left Loading Area"},{ "period":"Tele", "time":31.6, "event":"Piece Loaded"},{ "period":"Tele", "time":31.0, "event":"Left Loading Area"},{ "period":"Tele", "time":28.2, "event":"Enter Community 1"},{ "period":"Tele", "time":23.9, "event":"Score Cube Low"},{ "period":"Tele", "time":17.4, "event":"Left Community"},{ "period":"Tele", "time":17.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":17.0, "event":"Piece Loaded"},{ "period":"Tele", "time":16.9, "event":"Piece Loaded"},{ "period":"Tele", "time":16.4, "event":"Left Loading Area"},{ "period":"Tele", "time":12.3, "event":"Docked"},{ "period":"Tele", "time":10.2, "event":"Engaged"}],    "clockStopped":"2023/11/21 08:48:43.671",    "matchScore": {        "redAlliance":192,        "blueAlliance":253    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
#2910 Champ match 82c
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 1",    "team":2910,    "scoutName":"Kirk pncmp 82a",    "clockStarted":"2023/11/22 13:09:10.528",    "events":[{ "period":"Auto", "time":28.1, "event":"Score Cube High"},{ "period":"Auto", "time":26.1, "event":"Robot Moved"},{ "period":"Auto", "time":25.3, "event":"Floor Pickup"},{ "period":"Auto", "time":23.8, "event":"Score Cube Medium"},{ "period":"Auto", "time":23.4, "event":"Score Cube High"},{ "period":"Auto", "time":19.6, "event":"Floor Pickup"},{ "period":"Auto", "time":16.6, "event":"Score Cube Medium"},{ "period":"Tele", "time":131.3, "event":"Piece Loaded"},{ "period":"Tele", "time":129.1, "event":"Enter Community 1"},{ "period":"Tele", "time":127.9, "event":"Score Cube High"},{ "period":"Tele", "time":121.6, "event":"Left Community"},{ "period":"Tele", "time":119.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":116.1, "event":"Piece Loaded"},{ "period":"Tele", "time":115.0, "event":"Piece Loaded"},{ "period":"Tele", "time":114.4, "event":"Left Loading Area"},{ "period":"Tele", "time":110.8, "event":"Enter Community 1"},{ "period":"Tele", "time":108.2, "event":"Score Cube High"},{ "period":"Tele", "time":105.9, "event":"Left Community"},{ "period":"Tele", "time":104.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":102.3, "event":"Piece Loaded"},{ "period":"Tele", "time":100.8, "event":"Enter Community 3"},{ "period":"Tele", "time":99.6, "event":"Enter Community 1"},{ "period":"Tele", "time":96.2, "event":"Score Cube High"},{ "period":"Tele", "time":94.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":90.9, "event":"Left Community"},{ "period":"Tele", "time":87.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":87.0, "event":"Piece Loaded"},{ "period":"Tele", "time":86.0, "event":"Left Loading Area"},{ "period":"Tele", "time":82.1, "event":"Enter Community 1"},{ "period":"Tele", "time":79.1, "event":"Enter Community 1"},{ "period":"Tele", "time":76.1, "event":"Left Community"},{ "period":"Tele", "time":74.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":71.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":70.6, "event":"Piece Loaded"},{ "period":"Tele", "time":69.8, "event":"Left Loading Area"},{ "period":"Tele", "time":67.3, "event":"Enter Community 1"},{ "period":"Tele", "time":65.0, "event":"Score Cube High"},{ "period":"Tele", "time":64.8, "event":"Score Cube High"},{ "period":"Tele", "time":60.4, "event":"Left Community"},{ "period":"Tele", "time":57.9, "event":"Left Community"},{ "period":"Tele", "time":55.4, "event":"Piece Loaded"},{ "period":"Tele", "time":52.0, "event":"Enter Community 1"},{ "period":"Tele", "time":49.6, "event":"Score Cube High"},{ "period":"Tele", "time":47.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":47.4, "event":"Enter Loading Area"},{ "period":"Tele", "time":45.6, "event":"Enter Loading Area"},{ "period":"Tele", "time":42.7, "event":"Piece Loaded"},{ "period":"Tele", "time":41.3, "event":"Left Loading Area"},{ "period":"Tele", "time":39.8, "event":"Enter Community 1"},{ "period":"Tele", "time":36.8, "event":"Score Cube Low"},{ "period":"Tele", "time":32.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":28.4, "event":"Floor Pickup"},{ "period":"Tele", "time":25.4, "event":"Left Loading Area"},{ "period":"Tele", "time":23.9, "event":"Enter Community 1"},{ "period":"Tele", "time":20.1, "event":"Score Cube Low"},{ "period":"Tele", "time":15.6, "event":"Left Community"},{ "period":"Tele", "time":15.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":14.2, "event":"Piece Loaded"},{ "period":"Tele", "time":13.1, "event":"Enter Community 2"},{ "period":"Tele", "time":12.6, "event":"Enter Community 1"},{ "period":"Tele", "time":11.8, "event":"Score Cube High"},{ "period":"Tele", "time":7.3, "event":"Undocked"},{ "period":"Tele", "time":6.8, "event":"Docked"},{ "period":"Tele", "time":5.5, "event":"Disengaged"}],    "clockStopped":"2023/11/22 13:11:55.532",    "matchScore": {        "redAlliance":192,        "blueAlliance":153    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
#4513 Sun Dome
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 1",    "team":4513,    "scoutName":"Kirk pnw sun dome m22",    "clockStarted":"2023/11/22 13:33:46.588",    "events":[{ "period":"Auto", "time":19.8, "event":"Score Cube High"},{ "period":"Auto", "time":15.0, "event":"Left Community"},{ "period":"Tele", "time":126.5, "event":"Enter Loading Area"},{ "period":"Tele", "time":124.6, "event":"Piece Loaded"},{ "period":"Tele", "time":120.5, "event":"Human Bobble"},{ "period":"Tele", "time":119.3, "event":"Piece Loaded"},{ "period":"Tele", "time":117.8, "event":"Left Loading Area"},{ "period":"Tele", "time":114.6, "event":"Enter Community 1"},{ "period":"Tele", "time":108.7, "event":"Score Cone High"},{ "period":"Tele", "time":107.6, "event":"Score Cone Low"},{ "period":"Tele", "time":107.0, "event":"Left Community"},{ "period":"Tele", "time":103.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":99.1, "event":"Piece Loaded"},{ "period":"Tele", "time":97.0, "event":"Left Loading Area"},{ "period":"Tele", "time":94.5, "event":"Enter Community 3"},{ "period":"Tele", "time":88.1, "event":"Piece Dropped"},{ "period":"Tele", "time":86.0, "event":"Left Community"},{ "period":"Tele", "time":81.4, "event":"Piece Loaded"},{ "period":"Tele", "time":69.5, "event":"Score Cube High"},{ "period":"Tele", "time":67.7, "event":"Left Community"},{ "period":"Tele", "time":65.9, "event":"Enter Loading Area"},{ "period":"Tele", "time":60.4, "event":"Piece Loaded"},{ "period":"Tele", "time":59.6, "event":"Left Loading Area"},{ "period":"Tele", "time":56.5, "event":"Defended"},{ "period":"Tele", "time":55.8, "event":"Defending"},{ "period":"Tele", "time":55.0, "event":"Defended"},{ "period":"Tele", "time":53.8, "event":"Defended"},{ "period":"Tele", "time":51.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":48.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":43.0, "event":"Piece Dropped"},{ "period":"Tele", "time":39.1, "event":"Left Community"},{ "period":"Tele", "time":36.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":33.9, "event":"Left Loading Area"},{ "period":"Tele", "time":31.5, "event":"Enter Community 3"},{ "period":"Tele", "time":22.5, "event":"Score Cone High"},{ "period":"Tele", "time":18.6, "event":"Left Community"},{ "period":"Tele", "time":16.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":12.6, "event":"Piece Loaded"},{ "period":"Tele", "time":12.4, "event":"Piece Loaded"},{ "period":"Tele", "time":11.5, "event":"Left Loading Area"},{ "period":"Tele", "time":11.3, "event":"Left Loading Area"},{ "period":"Tele", "time":8.6, "event":"Score Cone Low"},{ "period":"Tele", "time":7.9, "event":"Enter Community 1"},{ "period":"Tele", "time":1.3, "event":"Docked"}],    "clockStopped":"2023/11/22 13:36:31.589",    "matchScore": {        "redAlliance":93,        "blueAlliance":65    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
#5920 pnchp match 100..doesn't reflect their defensive capabilities
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"blue 1",    "team":5920,    "scoutName":"Kirk pnw champ  match 100",    "clockStarted":"2023/11/26 09:50:22.216",    "events":[{ "period":"Auto", "time":27.3, "event":"Score Cube High"},{ "period":"Auto", "time":21.7, "event":"Left Community"},{ "period":"Tele", "time":130.5, "event":"Robot Moved"},{ "period":"Tele", "time":128.4, "event":"Floor Pickup"},{ "period":"Tele", "time":125.5, "event":"Floor Pickup"},{ "period":"Tele", "time":123.1, "event":"Floor Pickup"},{ "period":"Tele", "time":119.9, "event":"Enter Community 1"},{ "period":"Tele", "time":114.6, "event":"Score Cube Medium"},{ "period":"Tele", "time":112.2, "event":"Left Community"},{ "period":"Tele", "time":107.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":104.9, "event":"Piece Loaded"},{ "period":"Tele", "time":91.5, "event":"Score Cube Low"},{ "period":"Tele", "time":90.6, "event":"Left Community"},{ "period":"Tele", "time":88.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":86.0, "event":"Piece Loaded"},{ "period":"Tele", "time":83.4, "event":"Left Loading Area"},{ "period":"Tele", "time":44.6, "event":"Enter Community 1"},{ "period":"Tele", "time":39.9, "event":"Piece Dropped"},{ "period":"Tele", "time":36.5, "event":"Left Community"},{ "period":"Tele", "time":32.5, "event":"Piece Loaded"},{ "period":"Tele", "time":27.7, "event":"Left Loading Area"},{ "period":"Tele", "time":16.4, "event":"Enter Community 1"},{ "period":"Tele", "time":11.0, "event":"Docked"},{ "period":"Tele", "time":2.2, "event":"Engaged"}],    "clockStopped":"2023/11/26 09:53:07.213",    "matchScore": {        "redAlliance":146,        "blueAlliance":144    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
#5920 pnchp match 100..better some miss reporting
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"blue 1",    "team":5920,    "scoutName":"Kirk pnw champ  match 100",    "clockStarted":"2023/11/28 08:37:28.348",    "events":[{ "period":"Auto", "time":12.4, "event":"Score Cube High"},{ "period":"Auto", "time":3.5, "event":"Left Community"},{ "period":"Tele", "time":116.4, "event":"Enter Community 1"},{ "period":"Tele", "time":111.2, "event":"Score Cube Medium"},{ "period":"Tele", "time":109.0, "event":"Left Community"},{ "period":"Tele", "time":103.5, "event":"Enter Loading Area"},{ "period":"Tele", "time":96.6, "event":"Piece Loaded"},{ "period":"Tele", "time":95.8, "event":"Left Loading Area"},{ "period":"Tele", "time":93.4, "event":"Enter Community 1"},{ "period":"Tele", "time":87.2, "event":"Score Cube Low"},{ "period":"Tele", "time":86.5, "event":"Left Community"},{ "period":"Tele", "time":83.7, "event":"Enter Loading Area"},{ "period":"Tele", "time":79.7, "event":"Left Loading Area"},{ "period":"Tele", "time":78.4, "event":"Left Loading Area"},{ "period":"Tele", "time":73.2, "event":"Defending"},{ "period":"Tele", "time":72.5, "event":"Defending"},{ "period":"Tele", "time":70.6, "event":"Congestion"},{ "period":"Tele", "time":69.2, "event":"Congestion"},{ "period":"Tele", "time":67.7, "event":"Congestion"},{ "period":"Tele", "time":64.4, "event":"Defending"},{ "period":"Tele", "time":60.1, "event":"Left Community"},{ "period":"Tele", "time":57.5, "event":"Left Loading Area"},{ "period":"Tele", "time":56.5, "event":"Undocked"},{ "period":"Tele", "time":54.2, "event":"Defended"},{ "period":"Tele", "time":53.5, "event":"Defending"},{ "period":"Tele", "time":52.2, "event":"Defending"},{ "period":"Tele", "time":49.9, "event":"Congestion"},{ "period":"Tele", "time":44.3, "event":"Docked"},{ "period":"Tele", "time":39.4, "event":"Score Cube Low"},{ "period":"Tele", "time":38.4, "event":"Left Community"},{ "period":"Tele", "time":32.0, "event":"Docked"},{ "period":"Tele", "time":30.9, "event":"Defending"},{ "period":"Tele", "time":25.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":24.0, "event":"Piece Loaded"},{ "period":"Tele", "time":22.2, "event":"Left Loading Area"},{ "period":"Tele", "time":19.9, "event":"Defending"},{ "period":"Tele", "time":18.9, "event":"Congestion"},{ "period":"Tele", "time":18.0, "event":"Congestion"},{ "period":"Tele", "time":13.7, "event":"Enter Community 2"},{ "period":"Tele", "time":8.5, "event":"Left Community"},{ "period":"Tele", "time":4.4, "event":"Docked"},{ "period":"Tele", "time":2.2, "event":"Engaged"}],    "clockStopped":"2023/11/28 08:40:13.338",    "matchScore": {        "redAlliance":146,        "blueAlliance":144    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
#5920 pnchp match 100..better, good enough
JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"blue 1",    "team":5920,    "scoutName":"Kirk pnw champ  match 100",    "clockStarted":"2023/11/28 09:04:53.802",    "events":[{ "period":"Auto", "time":27.4, "event":"Score Cube High"},{ "period":"Auto", "time":23.9, "event":"Left Community"},{ "period":"Tele", "time":134.5, "event":"Robot Moved"},{ "period":"Tele", "time":134.1, "event":"Robot Moved"},{ "period":"Tele", "time":133.9, "event":"Robot Moved"},{ "period":"Tele", "time":130.1, "event":"Robot Moved"},{ "period":"Tele", "time":118.9, "event":"Piece Loaded"},{ "period":"Tele", "time":112.9, "event":"Score Cube Medium"},{ "period":"Tele", "time":111.2, "event":"Left Community"},{ "period":"Tele", "time":107.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":102.2, "event":"Piece Loaded"},{ "period":"Tele", "time":97.0, "event":"Left Loading Area"},{ "period":"Tele", "time":92.4, "event":"Enter Community 1"},{ "period":"Tele", "time":89.6, "event":"Score Cube Low"},{ "period":"Tele", "time":89.0, "event":"Left Community"},{ "period":"Tele", "time":85.9, "event":"Enter Loading Area"},{ "period":"Tele", "time":85.0, "event":"Piece Loaded"},{ "period":"Tele", "time":82.3, "event":"Left Loading Area"},{ "period":"Tele", "time":76.8, "event":"Defending"},{ "period":"Tele", "time":74.3, "event":"Defending"},{ "period":"Tele", "time":64.5, "event":"Enter Loading Area"},{ "period":"Tele", "time":63.4, "event":"Piece Loaded"},{ "period":"Tele", "time":57.9, "event":"Defending"},{ "period":"Tele", "time":55.9, "event":"Congestion"},{ "period":"Tele", "time":54.9, "event":"Congestion"},{ "period":"Tele", "time":54.1, "event":"Congestion"},{ "period":"Tele", "time":52.9, "event":"Defending"},{ "period":"Tele", "time":51.5, "event":"Defending"},{ "period":"Tele", "time":47.9, "event":"Enter Community 1"},{ "period":"Tele", "time":39.4, "event":"Piece Dropped"},{ "period":"Tele", "time":34.0, "event":"Defending"},{ "period":"Tele", "time":28.0, "event":"Enter Loading Area"},{ "period":"Tele", "time":26.7, "event":"Piece Loaded"},{ "period":"Tele", "time":26.0, "event":"Left Loading Area"},{ "period":"Tele", "time":20.2, "event":"Defending"},{ "period":"Tele", "time":16.5, "event":"Enter Community 3"},{ "period":"Tele", "time":12.8, "event":"Score Cube Low"},{ "period":"Tele", "time":9.0, "event":"Docked"},{ "period":"Tele", "time":1.2, "event":"Engaged"}],    "clockStopped":"2023/11/28 09:07:38.788",    "matchScore": {        "redAlliance":146,        "blueAlliance":144    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
#360 pnchp match 44
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 3",    "team":360,    "scoutName":"Kirk pnw champ 44",    "clockStarted":"2023/11/26 09:35:08.914",    "events":[{ "period":"Auto", "time":24.0, "event":"Score Cube High"},{ "period":"Auto", "time":20.1, "event":"Floor Pickup"},{ "period":"Auto", "time":15.4, "event":"Score Cube High"},{ "period":"Tele", "time":133.4, "event":"Robot Moved"},{ "period":"Tele", "time":124.5, "event":"Score Cube High"},{ "period":"Tele", "time":122.5, "event":"Left Community"},{ "period":"Tele", "time":120.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":116.1, "event":"Piece Loaded"},{ "period":"Tele", "time":115.1, "event":"Left Loading Area"},{ "period":"Tele", "time":113.5, "event":"Enter Community 1"},{ "period":"Tele", "time":109.4, "event":"Score Cone Medium"},{ "period":"Tele", "time":108.4, "event":"Left Community"},{ "period":"Tele", "time":106.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":103.9, "event":"Piece Loaded"},{ "period":"Tele", "time":103.1, "event":"Left Loading Area"},{ "period":"Tele", "time":96.6, "event":"Score Cube Medium"},{ "period":"Tele", "time":95.6, "event":"Left Community"},{ "period":"Tele", "time":94.0, "event":"Enter Loading Area"},{ "period":"Tele", "time":89.3, "event":"Piece Loaded"},{ "period":"Tele", "time":89.0, "event":"Left Loading Area"},{ "period":"Tele", "time":87.4, "event":"Enter Community 3"},{ "period":"Tele", "time":84.3, "event":"Score Cone Medium"},{ "period":"Tele", "time":83.1, "event":"Left Community"},{ "period":"Tele", "time":80.4, "event":"Piece Loaded"},{ "period":"Tele", "time":71.9, "event":"Piece Loaded"},{ "period":"Tele", "time":69.1, "event":"Enter Community 3"},{ "period":"Tele", "time":64.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":59.8, "event":"Left Community"},{ "period":"Tele", "time":58.0, "event":"Enter Loading Area"},{ "period":"Tele", "time":52.9, "event":"Left Loading Area"},{ "period":"Tele", "time":39.6, "event":"Score Cone High"},{ "period":"Tele", "time":38.3, "event":"Left Community"},{ "period":"Tele", "time":29.5, "event":"Enter Loading Area"},{ "period":"Tele", "time":27.7, "event":"Piece Loaded"},{ "period":"Tele", "time":25.2, "event":"Left Loading Area"},{ "period":"Tele", "time":23.1, "event":"Enter Community 3"},{ "period":"Tele", "time":17.0, "event":"Score Cone High"},{ "period":"Tele", "time":15.6, "event":"Left Community"},{ "period":"Tele", "time":9.8, "event":"Docked"},{ "period":"Tele", "time":8.2, "event":"Engaged"}],    "clockStopped":"2023/11/26 09:37:53.918",    "matchScore": {        "redAlliance":137,        "blueAlliance":181    },    "rankingPoints": {        "redAlliance":2,        "blueAlliance":4    }}'
#2910 pnchp match 82d
#JSON_STRING='{    "match":"1",    "redAlliance":[9999,5937,8051],    "blueAlliance":[3663,5941,2930],    "scoutingPosition":"red 1",    "team":2910,    "scoutName":"Kirk pnw champ 82",    "clockStarted":"2023/11/26 09:26:19.806",    "events":[{ "period":"Auto", "time":28.2, "event":"Score Cone High"},{ "period":"Auto", "time":27.8, "event":"Score Cube Medium"},{ "period":"Auto", "time":24.2, "event":"Floor Pickup"},{ "period":"Auto", "time":22.1, "event":"Score Cube High"},{ "period":"Auto", "time":19.3, "event":"Floor Pickup"},{ "period":"Auto", "time":16.7, "event":"Score Cube Medium"},{ "period":"Tele", "time":132.6, "event":"Robot Moved"},{ "period":"Tele", "time":127.9, "event":"Enter Loading Area"},{ "period":"Tele", "time":127.1, "event":"Piece Loaded"},{ "period":"Tele", "time":121.3, "event":"Score Cone High"},{ "period":"Tele", "time":119.7, "event":"Left Community"},{ "period":"Tele", "time":116.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":110.8, "event":"Enter Loading Area"},{ "period":"Tele", "time":109.5, "event":"Left Community"},{ "period":"Tele", "time":102.7, "event":"Score Cone High"},{ "period":"Tele", "time":101.5, "event":"Left Community"},{ "period":"Tele", "time":97.3, "event":"Piece Loaded"},{ "period":"Tele", "time":96.2, "event":"Piece Loaded"},{ "period":"Tele", "time":95.8, "event":"Left Loading Area"},{ "period":"Tele", "time":94.0, "event":"Enter Community 1"},{ "period":"Tele", "time":91.0, "event":"Score Cone High"},{ "period":"Tele", "time":89.5, "event":"Left Community"},{ "period":"Tele", "time":83.1, "event":"Piece Loaded"},{ "period":"Tele", "time":83.0, "event":"Piece Loaded"},{ "period":"Tele", "time":82.1, "event":"Left Loading Area"},{ "period":"Tele", "time":77.8, "event":"Enter Community 1"},{ "period":"Tele", "time":74.4, "event":"Score Cone High"},{ "period":"Tele", "time":72.3, "event":"Enter Loading Area"},{ "period":"Tele", "time":71.5, "event":"Piece Loaded"},{ "period":"Tele", "time":65.9, "event":"Enter Loading Area"},{ "period":"Tele", "time":65.1, "event":"Piece Loaded"},{ "period":"Tele", "time":64.6, "event":"Left Loading Area"},{ "period":"Tele", "time":62.5, "event":"Enter Community 1"},{ "period":"Tele", "time":57.6, "event":"Score Cone Medium"},{ "period":"Tele", "time":56.7, "event":"Left Community"},{ "period":"Tele", "time":53.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":51.2, "event":"Piece Loaded"},{ "period":"Tele", "time":50.1, "event":"Left Loading Area"},{ "period":"Tele", "time":47.6, "event":"Enter Community 1"},{ "period":"Tele", "time":43.6, "event":"Score Cube Medium"},{ "period":"Tele", "time":42.6, "event":"Left Community"},{ "period":"Tele", "time":41.1, "event":"Enter Loading Area"},{ "period":"Tele", "time":38.9, "event":"Piece Loaded"},{ "period":"Tele", "time":38.0, "event":"Left Loading Area"},{ "period":"Tele", "time":35.7, "event":"Enter Community 1"},{ "period":"Tele", "time":31.9, "event":"Score Cube Low"},{ "period":"Tele", "time":31.3, "event":"Left Community"},{ "period":"Tele", "time":29.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":26.3, "event":"Piece Loaded"},{ "period":"Tele", "time":24.3, "event":"Left Loading Area"},{ "period":"Tele", "time":22.1, "event":"Enter Community 2"},{ "period":"Tele", "time":17.4, "event":"Score Cube Low"},{ "period":"Tele", "time":16.3, "event":"Left Community"},{ "period":"Tele", "time":13.2, "event":"Enter Loading Area"},{ "period":"Tele", "time":10.3, "event":"Floor Pickup"},{ "period":"Tele", "time":8.4, "event":"Left Loading Area"},{ "period":"Tele", "time":4.3, "event":"Docked"},{ "period":"Tele", "time":2.0, "event":"Engaged"}],    "clockStopped":"2023/11/26 09:29:04.805",    "matchScore": {        "redAlliance":0,        "blueAlliance":0    },    "rankingPoints": {        "redAlliance":4,        "blueAlliance":2    }}'
match = MatchStat()
match.importJSON( JSON_STRING)
match.genMatchReport()





'''
    def genTeamReport( self):
        for each team in database:
            for each teamMatch data in database:
                add teamMatch data to summary
        generateTeamReport() 
        

    def generateMatchReport():
        System.println(f"team info")
        System.println(f"{match info} {timeToStartTeleOp}")
        System.println(f"{cycleNumber} {cycleTime} ")
        System.println(f"{cycles} {lowCycleTime} {aveCycleTime} {highCycleTime}")
'''
