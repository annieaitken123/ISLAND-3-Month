#coding: utf-8
#Import classes
from __future__ import division
from __future__ import print_function

import os
import pygaze
import pyglet
from pygaze import libtime
from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.keyboard import Keyboard
from pygaze.eyetracker import EyeTracker
from pygaze.logfile import Logfile
import pygaze.libtime as timer

from psychopy import visual, core, event


from psychopy.visual import MovieStim


#Netstation
# >>> import and initialization >>>

import egi.simple as egi
## import egi.threaded as egi

# ms_localtime = egi.egi_internal.ms_localtime
ms_localtime = egi.ms_localtime


ns = egi.Netstation()
ns.connect("10.10.10.42", 55513) # sample address and port -- change according to your network settings
## ns.initialize('11.0.0.42', 55513)
ns.BeginSession()

ns.sync()



# Initialise a Display instance, using the default settings.
# (You can add a constants.py file to set these defaults.)
disp = Display()

kb = Keyboard(keylist=['left','right','escape','space','return'], timeout=2000)

win = pygaze.expdisplay

globalClock = core.Clock()

# Create a screen to show instructions on.
textscr = Screen()
textscr.draw_text("Press any key to start the next video. Press Stim Start", fontsize=24)

# Initialise and calibrate an EyeTracker instance
tracker = EyeTracker(disp)
range=range(1,5)
for count in range:
    tracker.calibrate()
    key, presstime = kb.get_key(keylist=['escape', "Escape"], timeout=1, flush=False)
    if key in ['escape', 'Escape']:
        # Break the while loop.
        break

#Start EGI recording
ns.StartRecording()

movies = []
for movie_filename in ['Experiment.mp4', 'Resting_somesound.mp4', 'VPCstim4v.m4v']:
    movies.append(visual.MovieStim3(win, movie_filename, size=[1920,1080], flipVert=False))

for movie in movies:
    # Add the MovieStim to a PyGaze Screen instance.
    # (The Screen object has a list of all its associated
    # PsychoPy stimulus instances; you can add custom
    # instances, like the MovieStim, and they will automatically
    # be drawn each time you fill and show the Display.)
    movscr = Screen()
    movscr.screen.append(movie)

    # Wait until the participant presses any key to start.
    disp.fill(textscr)
    disp.show()
    kb.get_key(keylist=None, timeout=None, flush=True)


    # Start recording from the eye tracker.
    tracker.start_recording()

    # Record the starting time, and log it to the tracker.
    t1 = libtime.get_time()
    tracker.log('START;time=%d' % (t1))
    ns.send_event( 'evt_', label="start", timestamp=egi.ms_localtime(), table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042} )
    t0 = libtime.get_time()

#  Wait until the participant presses any key to start.
    while movie.status != visual.FINISHED:

        # Fill the Display with the Screen. The right
        # frame from the video will automatically
        # be selected by PsychoPy.
        disp.fill(movscr)
        # Show the Display, and record its onset
        t1 = disp.show()
        # Log the screen flip.
        tracker.log('FLIP; time=%d' % (t1))
        # Check if the Escape key was pressed.
        key, presstime = kb.get_key(keylist=['Escape', 'escape'], timeout=1, flush=False)
        if key in ['Escape', 'escape']:
            # Break the while loop.
            tracker.log('ESCAPE; time=%d' % (presstime))
            ns.send_event( 'evt_', label="esc", timestamp=egi.ms_localtime(), table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042} )
            break
    ns.send_event( 'evt_', label="end", timestamp=egi.ms_localtime(), table = {'fld1' : 123, 'fld2' : "abc", 'fld3' : 0.042} )

# Stop recording from the eye tracker.
tracker.log('END; time=%d' % (t1))
tracker.stop_recording()


#Stop recording from EEG
ns.StopRecording()

ns.EndSession()
ns.disconnect()


# Close the connection to the tracker.
tracker.close()

# Close the Display.
disp.close()
