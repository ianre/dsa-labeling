import os
import shutil
import json
import numpy as np
import pathlib

currentFilename = "file"

class Iterator:
    def __init__(self, task):
        self.CWD = os.path.dirname(os.path.realpath(__file__))        
        self.task = task
        self.taskSourceDir = os.path.join(self.CWD, "Experimental_Setup", self.task, "Balanced", "Gesture_Classification" )
        self.taskDestDir =  os.path.join(self.CWD, "DSA_Experimental_Setup", self.task, "Balanced", "Gesture_Classification" )
        

    def Format(self, debug=False):
        count = 0
        for root, dirs, files in os.walk(self.taskDir):
            for file in files:
                if "__objects" not in file: 
                    continue
                source = os.path.join(root, file)
                subdirname = os.path.basename(root)
                targetDir = os.path.join(self.taskOutput,subdirname)
                if(not os.path.isdir(targetDir)):
                    path = pathlib.Path(targetDir)
                    path.mkdir(parents=True, exist_ok=True)
                dest = os.path.join(targetDir, file)

                print(source, " : ", dest)
                F = Formatter( source, dest)
                F.loadJSON()
                F.formatToCOCO()
                #F.save()
                count += 1
                return;
        print(count)


    def Rename(self, cvScheme,  debug=False):
        count = 0
        print("Cross-validation Scheme: ", cvScheme)
        self.taskSourceDir = os.path.join(self.taskSourceDir, cvScheme)
        self.taskDestDir =  os.path.join(self.taskDestDir, cvScheme)
        print(self.taskSourceDir )
        for root, dirs, files in os.walk(self.taskSourceDir):
            for file in files:
                #if "__objects" not in file: 
                #    continue
                source = os.path.join(root, file)
                subdirname = os.path.basename(root)
                targetDir = os.path.join(self.taskDestDir,subdirname)

                if(not os.path.isdir(targetDir)):
                    path = pathlib.Path(targetDir)
                    path.mkdir(parents=True, exist_ok=True)

                dest = os.path.join(targetDir, file)
                #print(source)
                #print(dest)
                currentFilename = file
                #print(dest)
                #print()
                R = Renamer(source, dest)
                R.loadData()
                flag = R.Rename()    
                if flag:
                    print("found in ",dest)       
                #R.save()
                count += 1
                #if(count >= 10): return;
                #return
        print(count)

    def getcwd(self):
        return self.CWD

class Renamer:
    def __init__(self, txtLoc, txtTarget):
        self.txt_location = txtLoc    
        self.txt_target = txtTarget   

    def ProcessFilename(self, record):
        splits = record.split("_")
        #print(splits[1], self.ProcessID(splits[1]))
        splits[1] = self.ProcessID(splits[1])
        #ProcessID
        return "_".join(splits)

    def ProcessID(self, ID):
        subject = ID[0]
        trial = ID[2:]
        #print("Subject: ", subject, "    trial: ", trial)
        #name = "{}_{}".format(self.task, tokenized_sequence[-3])

        # K 7/28/2021 convert JIGSAWS subject/trial encoding into my encoding; kind-a-hack right now
        #subjecttrial = tokenized_sequence[-3]
        #subject = subjecttrial[0]
        #trial = subjecttrial[2:]
        if subject =="B":
            subject = 2
        elif subject == "C":
            subject = 3
        elif subject == "D":
            subject = 4
        elif subject == "E":
            subject = 5
        elif subject == "F":
            subject = 6
        elif subject == "G":
            subject = 7
        elif subject == "H":
            subject = 8
        elif subject == "I":
            subject = 9

        name = str("S0"+str(subject)+"_T"+str(trial))  # K 7/28/2021, subsequently I 9/15/2021
        #print(name)
        #print(name)
        return name

    def loadData(self):
        data = list()
        with open(self.txt_location) as file:
            while (line := file.readline().rstrip()):
                #print(line.split())
                data.append(line)
        self.data = data;

    def Rename(self):     
        flag = False;
        newLines = list()
        for line in self.data:
            newLine = self.ProcessFilename(line)
            #target = "Suturing_G001_S00_T1132_001225.txt           G5"
            target = "Suturing_S03_T05_000571_000676.txt           G2"
            #print(newLine)
            if newLine.strip() == target.strip():
                #print("FOUND : ", newLine, " in " , currentFilename )
                flag = True

            newLines.append(newLine)
            #print(newLine)  
        self.newLines = newLines   
        return flag

    def save(self):        
        #with open(self.txt_target, "w+") as targetFile:
        #    json.dump(self.coco_format, jsonFile)
        with open(self.txt_target, "w+") as targetFile:
            #targetFile.write(str(values))
            targetFile.write('\n'.join(self.newLines))
        #print(os.listdir(dest))
        #print("saving ", self.txt_target, " with data ")

class Formatter:
    def __init__(self, jsonLoc, jsonTarget):
        self.json_location = jsonLoc    
        self.json_target = jsonTarget        
    def loadJSON(self):
        with open(self.json_location) as f:
            data = json.load(f)
            self.data = data
            self.meta = data['metadata']
            self.instances = data['instances']
    def formatToCOCO(self):       
        labels = list()
        for instance in self.instances:            
            instance_ID = instance["classId"]
            instance_type = instance["type"]
            instance_probability = instance["probability"]
            instance_class = instance["className"]
            if(instance_type == "point"):                
                label = {
                    "id" : instance_ID,
                    "type" : instance_type,
                    "probability" : instance_probability,
                    "point" : [instance["x"], instance["y"]],
                    "className" : instance_class,   
                }          
            else:
                instance_points = instance["points"]
                label = {
                    "id" : instance_ID,
                    "type" : instance_type,
                    "probability" : instance_probability,
                    "points" : instance_points,
                    "className" : instance_class, 
                }
            
            labels.append(label)            
        coco_format = {
            "name" : self.meta["name"],
            "annotations" : labels,
        }        
        self.coco_format = coco_format         
    def format(self, file):
        if (not file):
            print("file not found", file, " using ", self.data, "instead")
        print(file)
        count = 1   
        for image in data['images']:            
            filename = image['file_name']
            json_annote = os.path.join(filename[:-4]+"json")
            #print(json_annote)
            with open(json_annote) as file:
                annotations = json.load(file)
            for annotation in annotations['annotations']:
                #print(annotation)
                c_id =  annotation['name']
                obj_id = 0
                if c_id=="Left-Grasper":
                    obj_id = 302802
                elif c_id=="Right-Grasper":
                    obj_id = 302803
                elif c_id=="Needle End":
                    obj_id = 302804
                elif c_id=="Needle Tip":
                    obj_id= 302805
                # add to this: data["annotations"]
                if c_id == "Left-Grasper" or c_id == "Right-Grasper":
                    annote_string = []
                    max_y = 0 
                    max_x = 0
                    min_x = 1000
                    min_y = 1000 
                    
                    for path in annotation['polygon']['path']:
                        x = int(path['x'])
                        y = int(path['y'])
                        max_y = np.maximum(y, max_y)
                        min_y = np.minimum(y, min_y)

                        max_x = np.maximum(x, max_x)
                        min_x = np.minimum(x, min_x)

                        annote_string.append(int(x))
                        annote_string.append(int(y))
                        annote_s = []
                        annote_s.append(annote_string)
                    data['annotations'].append({"category_id":obj_id, "image_id":image['id'], "segmentation":annote_s, "id":count, "bbox":[int(min_x),int(min_y),int(max_x-min_x),int(max_y-min_y)], "iscrowd":0})
                    count+=1
                else:
                    x = int(annotation['keypoint']['x'])
                    y = int(annotation['keypoint']['y'])
                    annote_string = []
                    for i in range(0,3):
                        annote_string.append(int(x-(i+1)))
                        annote_string.append(int(y+i))
                    annote_s = []
                    annote_s.append(annote_string)
                    data['annotations'].append({"category_id":obj_id, "image_id":image['id'], 'segmentation':annote_s, "id":count, "bbox":[int(x),int(y),2,2], "iscrowd":0})
                    count+=1            
    def show(self):
        print(self.data)    
    def save(self):        
        with open(self.json_target, "w+") as jsonFile:
            json.dump(self.coco_format, jsonFile)

        #print(os.listdir(dest))
        print("saving ", self.json_target, " with data ", self.coco_format)

Ioto = Iterator("Suturing") # or suturing, needle_passing
Ioto.Rename("OneTrialOut", debug=True)
Iuo = Iterator("Suturing") # or suturing, needle_passing
Iuo.Rename("UserOut", debug=True)
Isto = Iterator("Suturing") # or suturing, needle_passing
Isto.Rename("SuperTrialOut", debug=True)
quit();
