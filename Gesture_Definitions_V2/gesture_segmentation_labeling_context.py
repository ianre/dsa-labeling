# Kay Hutchinson 8/25/2021
#
# For labing the videos in the JIGSAWS, DESK, ROSMA, and V-RASTED datasets
# using my new gesture definitions based on context.
#

import os, sys, glob, cv2
from tkinter import *
import PIL
from PIL import Image
from PIL import ImageTk

global frameNum
global run

# List of objects and states
objects = ["Nothing", "Ball/Block/Sleeve", "Needle", "Thread", "Fabric/Tissue", "Ring", "Other"]
needleStates = ["Not in", "In"]
threadStates = ["Loose", "Taut"]
cLoopStates = ["Not formed", "Formed"]
knotStates = ["Loose", "Tight"]

# App code
# From https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.task = window_title[:-8]  # retrieve task name from window_title
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Set up layout of widgets
        self.top1 = Frame(window)
        self.top1.pack(side=TOP,expand=True)
        self.top2 = Frame(window)
        self.top2.pack(expand=True)
        self.middle1 = Frame(window)
        self.middle1.pack(expand=True)
        self.middle2 = Frame(window)
        self.middle2.pack(expand=True)
        self.middle3 = Frame(window)
        self.middle3.pack(expand=True)
        self.middle4 = Frame(window)
        self.middle4.pack(expand=True)
        self.middle5 = Frame(window)
        self.middle5.pack(expand=True)
        self.middle6 = Frame(window)
        self.middle6.pack(expand=True)
        self.middle7 = Frame(window)
        self.middle7.pack(expand=True)
        self.middle8 = Frame(window)
        self.middle8.pack(expand=True)
        self.bottom1 = Frame(window)
        self.bottom1.pack(expand=True)
        self.bottom2 = Frame(window)
        self.bottom2.pack(expand=True)
        self.bottom3 = Frame(window)
        self.bottom3.pack(side=BOTTOM, expand=True)


        # Note to not use x button to close window
        self.warning = Text(window, width=37, height=1)
        self.warning.insert(END,"DO NOT close window, use QUIT button")
        self.warning.pack(in_=self.top1, side=RIGHT, anchor=E)

        # Create a canvas that can fit the above video source size
        w = int((480.0/self.vid.height)*self.vid.width)
        self.canvas = Canvas(window, width = w, height = 480)  #self.vid.width, height = self.vid.height)
        self.canvas.pack(in_=self.top2, expand=True)


        # Drop down menus for L/R graspers holding/contacting objects
        textBoxWidth = 40
        textBoxWidth2 = 20
        menuBoxWidth = 15

        self.LHold = Text(window, width=textBoxWidth, height=1)
        self.LHold.insert(END, "The Left Grasper is holding ")
        self.LHold.pack(in_=self.middle1, side=LEFT)
        self.LH = StringVar(window)
        self.LH.set(objects[0])  # set default
        self.LHoldOpts = OptionMenu(window, self.LH, *objects)
        self.LHoldOpts.config(width=menuBoxWidth)
        self.LHoldOpts.pack(in_=self.middle1, side=RIGHT)

        self.LContact = Text(window, width=textBoxWidth, height=1)
        self.LContact.insert(END, "The Left Grasper is in contact with ")
        self.LContact.pack(in_=self.middle2, side=LEFT)
        self.LC = StringVar(window)
        self.LC.set(objects[0])  # set default
        self.LContactOpts = OptionMenu(window, self.LC, *objects)
        self.LContactOpts.config(width=menuBoxWidth)
        self.LContactOpts.pack(in_=self.middle2, side=RIGHT)

        self.RHold = Text(window, width=textBoxWidth, height=1)
        self.RHold.insert(END, "The Right Grasper is holding ")
        self.RHold.pack(in_=self.middle3, side=LEFT)
        self.RH = StringVar(window)
        self.RH.set(objects[0])  # set default
        self.RHoldOpts = OptionMenu(window, self.RH, *objects)
        self.RHoldOpts.config(width=menuBoxWidth)
        self.RHoldOpts.pack(in_=self.middle3, side=RIGHT)

        self.RContact = Text(window, width=textBoxWidth, height=1)
        self.RContact.insert(END, "The Right Grasper is in contact with ")
        self.RContact.pack(in_=self.middle4, side=LEFT)
        self.RC = StringVar(window)
        self.RC.set(objects[0])  # set default
        self.RContactOpts = OptionMenu(window, self.RC, *objects)
        self.RContactOpts.config(width=menuBoxWidth)
        self.RContactOpts.pack(in_=self.middle4, side=RIGHT)


        # Task specific context
        if (self.task == "Suturing") or (self.task == "Needle_Passing"):
            # Needle [not in/in] fabric or ring
            self.Needle = Text(window, width=textBoxWidth2, height=1)
            self.Needle.insert(END, "The needle is ")
            self.Needle.pack(in_=self.middle5, side=LEFT)
            self.N = StringVar(window)
            self.N.set(needleStates[0])
            self.NeedleOpts = OptionMenu(window, self.N, *needleStates)
            self.NeedleOpts.config(width=menuBoxWidth)
            self.NeedleOpts.pack(in_=self.middle5, side=LEFT)
            self.Needle2 = Text(window, width=textBoxWidth2, height=1)
            if self.task == "Suturing":
                self.Needle2.insert(END, " fabric.")
            elif self.task == "Needle_Passing":
                self.Needle2.insert(END, "ring.")
            self.Needle2.pack(in_=self.middle5, side=RIGHT)

            # Thread [loose/taut]
            self.Thread = Text(window, width=textBoxWidth2, height=1)
            self.Thread.insert(END, "The thread is ")
            self.Thread.pack(in_=self.middle6, side=LEFT)
            self.T = StringVar(window)
            self.T.set(threadStates[0])
            self.ThreadOpts = OptionMenu(window, self.T, *threadStates)
            self.ThreadOpts.config(width=menuBoxWidth)
            self.ThreadOpts.pack(in_=self.middle6, side=LEFT)

        elif self.task == "Knot_Tying":
            # C-loop [not formed/formed]
            self.cLoop = Text(window, width=textBoxWidth2, height=1)
            self.cLoop.insert(END, "The c-loop is ")
            self.cLoop.pack(in_=self.middle7, side=LEFT)
            self.C = StringVar(window)
            self.C.set(cLoopStates[0])
            self.cLoopOpts = OptionMenu(window, self.C, *cLoopStates)
            self.cLoopOpts.config(width=menuBoxWidth)
            self.cLoopOpts.pack(in_=self.middle7, side=LEFT)

            # Knot [loose/tight]
            self.Knot = Text(window, width=textBoxWidth2, height=1)
            self.Knot.insert(END, "The knot is ")
            self.Knot.pack(in_=self.middle8, side=LEFT)
            self.K = StringVar(window)
            self.K.set(knotStates[0])
            self.KnotOpts = OptionMenu(window, self.K, *knotStates)
            self.KnotOpts.config(width=menuBoxWidth)
            self.KnotOpts.pack(in_=self.middle8, side=LEFT)


        # Enter button to confirm choice
        self.enter = Button(window,text="Save frame and continue",width=30, font='sans 15',command=self.mark)
        self.enter.pack(in_=self.bottom2,anchor=CENTER)

        # Done button to finish video
        self.done=Button(window,text="Next video", width=15, font='sans 15',command=self.done)
        self.done.pack(in_=self.bottom2, anchor=CENTER)

        # Quit button to close properly
        self.quit=Button(window,text="Quit", font='sans 15',command=self.quit)
        self.quit.pack(in_=self.bottom3, anchor=CENTER)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()


    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        nextImg = PIL.Image.fromarray(frame)

        # Scale new image to height of 480 px, keep ratio
        width, height = nextImg.size
        scaling = 480.0/height  # scale to height of 480 px
        newwidth = int(scaling*width)
        nextImg=nextImg.resize((newwidth, 480))

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = nextImg)
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

        self.window.after(self.delay, self.update)

    def mark(self):
        global frameNum

        # Write encoded context to transcript .txt file
        t.write(str(frameNum) + " ") # frame number
        t.write(str(objects.index(self.LH.get())) + " " + str(objects.index(self.LC.get())) + " ")  # left grasper
        t.write(str(objects.index(self.RH.get())) + " " + str(objects.index(self.RC.get())) + " ")  # right grasper

        if (self.task == "Suturing") or (self.task == "Needle_Passing"):
            t.write(str(needleStates.index(self.N.get())) + " ") # needle state
            t.write(str(threadStates.index(self.T.get())))       # thread state
        elif self.task == "Knot_Tying":
            t.write(str(cLoopStates.index(self.C.get())) + " ") # c loop state
            t.write(str(knotStates.index(self.K.get())))       # knot state

        t.write("\n")


        '''
        # Save image
        ret, frame = self.vid.get_frame()
        if ret:
            img1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            imgpil = ImageTk.getimage( img1 )
            rgb_im = imgpil.convert('RGB')
            rgb_im.save(os.path.join(dir,"Transitions", str(frameNum)+".jpg"), "JPEG" )
        '''

        frameNum = frameNum + 15
        # if end of video, close window
        if frameNum > self.vid.length:
            t.close()
            self.window.destroy()

    def done(self):
        t.close()
        self.window.destroy()

    def quit(self):
        global run
        # Delete unfinished transcript
        t.close()
        os.remove(t.name)
        self.window.destroy()
        run = 0

class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # Get video length in frames
        self.length = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_frame(self):
        if self.vid.isOpened():
            self.vid.set(1, frameNum)
            ret, frame = self.vid.read()
            if ret:
                '''
                # Scale new image to height of 480 px, keep ratio
                nextImg=frame
                scaling = 480/self.height  # scale to height of 480 px
                newwidth = int(scaling*self.width)
                #nextImg.resize((newwidth, 480))
                frame=cv2.resize(frame, (newwidth, 480), interpolation=cv2.INTER_AREA)
                '''
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()



# MAIN -------------------------------------------------------------------------
# Location of dataset folder
dir=os.getcwd()

# Get task from command line
try:
    task=sys.argv[1]
    #print(task)
except:
    print("Error: invalid task\nUsage: python gesture_segmentation_labeling.py <task>\nTasks: Suturing, Needle_Passing, Knot_Tying, Pea_on_a_Peg, Post_and_Sleeve, Wire_Chaser_I, Peg_Transfer")
    sys.exit()

# Transcript and video directories
taskDir = os.path.join(dir, "Datasets", "dVRK", task)
transcriptDir = os.path.join(taskDir,"transcriptions")
videoDir = os.path.join(taskDir,"video")

# List of finished transcripts
doneList = [done.split('/')[-1].rsplit(".txt")[0] for done in glob.glob(transcriptDir+'/*.txt')]
#print(doneList)

# Set to run
run = 1

# For each video ending in "_capture1.avi" or ".mp4"
videos = glob.glob(videoDir+"/*.avi") + glob.glob(videoDir+"/*.mp4")
for video in videos:

    trial = video.split("/")[-1]
    # Get name for transcript file name
    trialName = trial.rsplit("_",1)[0]

    if task in ["Pea_on_a_Peg", "Post_and_Sleeve", "Wire_Chaser_I"]:   # single camera videos need different rsplit indexing
        #trialName = trial.rsplit(".")[0]
        trialName = trial.rsplit(".")[0]

    if trialName in doneList:
        continue

    transcriptName = trialName+".txt"
    transcriptPath = os.path.join(transcriptDir, transcriptName)
    print("Working on: "+trialName)

    # Init frameNum counter
    frameNum = 0
    startFrame = 0

    # Create transcript file for this video
    t = open(transcriptPath, 'w')
    #t.write("0 ")

    # Run app
    App(Tk(), trialName, video)

    # Closes all the frames
    t.close()
    cv2.destroyAllWindows()

    if run == 0:
        break


    #print(transcriptPath)

# end
