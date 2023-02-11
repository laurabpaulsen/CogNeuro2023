""" DESCRIPTION:
This combined EEG and mouse tracking experiment displays two stimuli on either side of the screen. Before this presentation a word indicates what the participant should click on. The stimuli can either be neutral (line-drawings), color congruent, or color incongruent (color of stimuli switched around). 

/Code written by Laura Bock Paulsen 2022, adapted from a OpenSesame experiment by Jessica Clarke and Sille Hasselbalch.

Structure of this script:
    IMPORT MODULES 
    DEFINE HELPER FUNCTIONS
    GET PARTICIPANT INFO USING GUI
    PREPARE LOG FILES
    SPECIFY TIMING AND MONITOR
    LOADING IN EXPERIMENTAL DETAILS
    FUNCTION FOR EXPERIMENTAL LOOP
    DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
    CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP

"""
# IMPORT MODULES
from psychopy import core, visual, event, gui, monitors
import pandas as pd
from datetime import datetime
import csv
import os
from triggers import setParallelData


# Experimental parameters
RETINA = True  # Set to True if you are using a mac with retina display, set to False if you are using a different operating system or a mac without retina display

# Monitor parameters
MON_DISTANCE = 60  # Distance between subject's eyes and monitor 
MON_WIDTH = 20  # Width of your monitor in cm
MON_SIZE = [1440, 900]  # Pixel-dimensions of your monitor
FRAME_RATE = 60 # Hz


# GET PARTICIPANT INFO USING GUI
# ------------------------------
# Intro-dialogue. Get subject-id and other variables.
# Save input variables in "V" dictionary (V for "variables")
V = {'ID':'','gender':['female','male','other'],'age':''}
if not gui.DlgFromDict(dictionary = V, title = 'EEG and Mousetracking Experiment').OK: # dialog box; order is a list of keys 
    core.quit()


# PREPARE LOG FILES
# -----------------
now = datetime.now()
utc_time = now.strftime("%H_%M_%S")

save_path = os.path.join('data', V['ID'] + '_' + utc_time + '.csv')

list_of_columns = ['ID', 'age', 'gender', 'word', 'category', 'word_trigger','right_img', 'left_img','img_trigger','onset_word', 'onset_img', 'correct_resp','trial_type','trial_number', 'ypos', 'xpos', 'rt', 'key_t', 'response', 'accuracy', 'trial_timestamp']
csvfile = open(save_path,'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames = list_of_columns)
writer.writeheader()

"""
SPECIFY TIMING AND MONITOR
"""

# Clock and timer
clock = core.Clock()  # A clock wich will be used throughout the experiment to time events on a trial-per-trial basis (stimuli and reaction times).

# Create psychopy window
my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)  # Create monitor object from the variables above. This is needed to control size of stimuli in degrees.
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor = my_monitor, units = 'deg', fullscr=True, allowGUI=True, color='black')  # Initiate psychopy Window as the object "win", using the myMon object from last line. Use degree as units!

# Prepare Fixation cross
stim_fix = visual.TextStim(win, '+', alignText = 'center')
stim_fix_low = visual.TextStim(win, '+', pos=[0.0, -1.1]) # FIX THIS SHIT

'''
LOADING IN EXPERIMENTAL DETAILS
'''
# Load in csv's with details about trials
experimental_path = os.path.join('experimental_details', 'experimental_info.csv')
experimentaldf = pd.read_csv(experimental_path, sep = ';')

# Randomizing the order of the rows
experimentaldf = experimentaldf.sample(frac=1).reset_index(drop=True)

# The word stimulus 
stim_text = visual.TextStim(win=win, pos=[0,0], height=0.7, alignText='center')

# The image size and position using ImageStim, file info added in trial list below.
stim_left_pos = (-5.5, 3)
stim_right_pos = (5.5, 3)
stim_size = (7, 5)


stim_image_left = visual.ImageStim(win,
    mask=None,
    pos=stim_left_pos,
    size=stim_size,
    ori=1)

stim_image_right = visual.ImageStim(win,
    mask=None,
    pos=stim_right_pos,
    size=stim_size,
    ori=1)

if not RETINA:
    button_left = visual.Rect(win, size = stim_size, pos = stim_left_pos, fillColor = 'blue', opacity = 0.0)
    button_right = visual.Rect(win, size = stim_size, pos = stim_right_pos, fillColor = 'red', opacity = 0.0)

else:  # for some reason there is a discrepancy between the measured mouse location and where the stimuli is shown with some retina screens. This is a workaround.
    button_left = visual.Rect(win, size = (12,9.5), pos = (10,5), fillColor = 'green', opacity = 0.0)
    button_right = visual.Rect(win, size = (-12,9.5), pos = (-10,5), fillColor = 'yellow', opacity = 0.0)

# Mouse
mouse = event.Mouse(visible=True, win=win)

KEYS_QUIT = ['escape','q']  # Keys that quits the experiment

MAX_LENGTH_TRIAL = 500 # The maximum number of frames in each trial


'''
FUNCTION FOR EXPERIMENTAL LOOP
'''
def make_trial_list(trial_df):
    trial_list = []
    
    for i in range(len(trial_df)):
        data = trial_df.loc[i]

        # Define the trigger codes
        if data['trial_type'] == 'neutral':
            TRIG_I = 11
            TRIG_W = 12
        if data['trial_type'] == 'congruent':
            TRIG_I = 21
            TRIG_W = 22
        if data['trial_type'] == 'incongruent':
            TRIG_I = 31
            TRIG_W = 32
            
        # Add a dictionary for every trial
        trial_list += [{
            'ID': V['ID'],
            'age': V['age'],
            'gender': V['gender'],
            'word':data['task'],
            'category':data['category'],
            'word_trigger':TRIG_W,
            'right_img': os.path.join('stimuli', data['right_image']),
            'left_img': os.path.join('stimuli', data['left_image']),
            'img_trigger':TRIG_I,
            'onset_word':'',
            'onset_img':'',
            'response': '',
            'key_t':'',
            'rt': '',
            'correct_resp': data['correct_response'],
            'accuracy': '',
            'trial_type':data['trial_type'],
            'trial_number': i + 1,
            'trial_timestamp': '',
            'xpos': '',
            'ypos': ''
        }]
    return trial_list



def run_experiment(trial_list, exp_start):
    """
    Runs a block of trials. This is the presentation of stimuli,
    collection of responses and saving the trial
    """
    # Creating empty list to log mouse positions and timestamps in
    x_pos_list = []
    y_pos_list = []
    timestamp_list = []

    # Set EEG trigger in off state
    pullTriggerDown = False
    # Loop over trials
    for trial in trial_list:
        mouse.setPos(newPos = [0.0, -9])
        event.clearEvents()# clear input to make sure that no responses are logged that do not belong to stimulus
        
        # prepare word
        stim_text.text = trial['word']
        time_flip_word = core.monotonicClock.getTime() #onset of stimulus

        for frame in range(60):
            stim_text.draw()
            if frame==1: # pulls trigger or prints trigger code in frame 1
                win.callOnFlip(setParallelData, trial['word_trigger'])  
                pullTriggerDown = True
            win.flip()

            if pullTriggerDown: 
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False

        # Display fixation cross
        for frame in range(12):
            stim_fix_low.draw()

        # Prepare images
        stim_image_right.image = trial['right_img']
        stim_image_left.image = trial['left_img']


        # Display images and monitor time + ensure mouse starts in the same place
        mouse.setPos(newPos = [0.0, -9])
        time_flip_img = core.monotonicClock.getTime() #onset of stimulus
        for frame in range(MAX_LENGTH_TRIAL):
            stim_image_right.draw()
            stim_image_left.draw()
            button_right.draw()
            button_left.draw()


            if frame==1:
                win.callOnFlip(setParallelData, trial['img_trigger']) 
                pullTriggerDown = True

            win.flip()

            if pullTriggerDown:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False

            #Log values
            trial['onset_word'] = time_flip_word-exp_start
            trial['onset_img'] = time_flip_img-exp_start

            #Log values for mouse
            x_pos_list.append(mouse.getPos()[0])
            y_pos_list.append(mouse.getPos()[1])

            #Log trial timestamp
            time_trial = core.monotonicClock.getTime()
            timestamp_list.append(time_trial - time_flip_img)
            
        

            # checking for mouse clicks on stimuli
            buttons = mouse.getPressed()
            if mouse.isPressedIn(button_left):
                if (buttons == [1, 0, 0] and button_left.contains(mouse.getPos())):
                    time_click = core.monotonicClock.getTime() 
                    trial['response'] = 'left'
                    trial['key_t']=time_click-exp_start
                    trial['rt'] = time_click-time_flip_img
                break # break out of loop and go to next trial

            elif mouse.isPressedIn(button_right):
                if (buttons == [1, 0, 0] and button_right.contains(mouse.getPos())):
                    time_click = core.monotonicClock.getTime() 
                    trial['response'] = 'right'  
                    trial['key_t']=time_click - exp_start
                    trial['rt'] = time_click - time_flip_img
                break # break out of loop and go to next trial


        # Display fixation cross
        for frame in range(30): # Pause after each trial with fixation cross
            stim_fix.draw()
            win.flip()
                   

        #check if responses are correct
        if trial['response']=='right':
            trial['accuracy'] = 1 if trial['correct_resp']=='right' else 0
        elif trial['response']=='left':
            trial['accuracy'] = 1 if trial['correct_resp']=='left' else  0

        key = event.getKeys(keyList=('escape','q'))
        if key in KEYS_QUIT:
            win.close()
            core.quit()
        

        # save csv with trial data
        trial['xpos'] = x_pos_list
        trial['ypos'] = y_pos_list
        trial['trial_timestamp'] = timestamp_list
        writer.writerow(trial)
            
        
    
'''
DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
'''

# Define text objects
welcome_text= "Welcome to this experiment!\n\n\
The data collected will be used for a Cognitive Science exam project.\n\n\
Your data will be anonymised.\n\n\
By continuing you consent to your data being used for this purpose. It will not be used for other purposes.\n\n\
\n\n\
Press any key to continue."

instructions_text="Your task is to click on the specified \n\n\
item as fast as possible using the computer mouse provided. \n\n\
The mouse cursor will return to the same starting point after every trial. \n\n\
\n\n\
EXAMPLE: \n\n\
A specified item could be ZEBRA. \n\n\
Then your task is to click on the Zebra with the computer mouse. \n\n\
Press any key to continue."

goodbye_text="The experiment is now done.\n\n\
Thank you for participating!\n\n\
\n\n\
Press any key to exit."

#Function for showing welcome/goodbye text and waiting for key press
def msg(txt):
    message = visual.TextStim(win, text = txt, height = 0.5)
    message.draw()
    win.flip()
    core.wait(1.5)
    event.waitKeys()

#Show instructions
msg(welcome_text)
msg(instructions_text)

exp_start=core.monotonicClock.getTime()

'''
CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP
'''
for frame in range(1*FRAME_RATE):
     stim_fix.draw()
     win.flip()

trial_list = make_trial_list(trial_df = experimentaldf)
run_experiment(trial_list, exp_start)


csvfile.close()

msg(goodbye_text)