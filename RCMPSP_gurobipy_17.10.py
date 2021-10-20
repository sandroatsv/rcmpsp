##1. import gurobi

from gurobipy import *  

#
##2. declare the model RCMPSP

model = Model("RCMPSP")       


##3. define data

#number pf projects
project = range (3)

#number of activities per project
activity = range (4)

#number ob resourcetypes
resourcetype = range (2)

#number of timeunits
timeunit = range (15)


#in every time period t available units of resource type k=1,2 to execute the activities of each project for each time period:
ra = [[15,15],
      [10,10],
      [15,15],
      [14,8],
      [10,0],
      [3,10],
      [3,10],
      [14,3],
      [5,8],
      [13,9],
      [4,10],
      [14,12],
      [3,10],
      [20,10],
      [20,1],
      ]
       
#variable costs using 1 unit of resource type k=1,2 for all t's, in all activities, in all projects:
rc = [95, 50]
#extension factor of the number of resources needed to perform the activity in the same time due to using another resource type k=1,2 for all t's, in all activities, in all projects:
ref=  [1, 2]
#var costs per not.used unit of each resource type k:
cur = [25, 15]

#fix costs fixcpp for each project that are charged if the corresponding project is paused (no activity of the coresponding project is running) in a time period:
cpnr = [100, 100, 100]


#durations of the execution of each activity of each project i=1,2,3:
du = [  [3, 5, 2, 4],
        [3, 4, 2, 4],
        [3, 4, 1, 4]
     ]

#until this time the 2nd, 3rd and 4th activities cannot be started
timeact1 = range (4)
timeact2 = range (4)
timeact3 = range (6)
timeact4 = range (9)




#quantity of resource units needed to carry out an activity of a project in averga in a timeunit:
rn = [   [3, 4, 5, 3],
         [3, 1, 3, 7],
         [3, 6, 2, 6]
     ]  

# only one precedessor per acitivity; first activity of a project doesn't  have any preprosessor!!
precedence = [[[0,1,1,1], [0,0,1,1], [0,0,0,1], [0,0,0,0]], #e.g. first range in first row and first column [0,1,1,1]: activity j=1 of project i=1 is precedessor of activities j=2,3,4 of project 1
              [[0,1,1,1], [0,0,1,1], [0,0,0,1], [0,0,0,0]],
              [[0,1,1,1], [0,0,1,1], [0,0,0,1], [0,0,0,0]]
             ]


##4. create variables:

#activity j of project i executed with resource type k in time period t? er as binary variable! er[1,2,1,2] = 1: in time unit 1, activity 2 of project 1 should be executed with resourcetype 2 
er = model.addVars(timeunit, project, activity, resourcetype, vtype=GRB.BINARY)

#resources used due to the execution of activity j in project i with resourcetype k in time unit t
ru = model.addVars(timeunit, project, activity, resourcetype)

#summed number of ressurces used in each time unit of each resource type
rutk = model.addVars(timeunit, resourcetype)

#summed number of resources used in each time unit
rut = model.addVars(timeunit)

#summed number of resources used in each time unit per project:
ruti = model.addVars(timeunit, project)

#pnr: decision variable (binary); is project i running in t? (=are resources used by project i to execute aktivities in t?): pnr=1 if the amount of used resources by the project in that timeunit is = 0!, else npr=0 for the project in that timeunit!
pnr = model.addVars(timeunit, project, vtype=GRB.BINARY)


model.update()


#5: create objective function: 
    
#total costs have to be minimized; costs due to the use of resources: costs for the use of resources summed up over all projects and time units + Costs for unused resources summed over all projects and all time units + Costs if a project doens't execute any activity in one timeunit summed over all projects and all time units (Korrekt)                                   
model.setObjective(sum(ru[t,i,j,k] * rc[k] for t in timeunit for i in project for j in activity for k in resourcetype) + sum(ra[t][k] * cur[k] - rutk[t,k] * cur[k] for t in timeunit for k in resourcetype) + sum(pnr[t,i] * cpnr[i] for t in timeunit for i in project), GRB.MINIMIZE)


#6: create constraints:      

#1. every activity of every project can only be executed with one resource type in every time period!! (Korrekt) 
model.addConstrs(sum(er[t,i,j,k] for k in resourcetype) <= 1 for i in project for j in activity for t in timeunit)

#2. every activity of every project has to be executed as many times within t according to its duration!! (Korrekt)
model.addConstrs(sum(er[t,i,j,k] for t in timeunit for k in resourcetype) == du[i][j] for i in project for j in activity) 

#3. if an activity isn't executed (er=0): amount of resources used == 0; if an activity is executed (er=1): resources used are equal to (resource need * resource extension factor): (Korrekt)
model.addConstrs(ru[t,i,j,k] == er[t,i,j,k] * rn[i][j] * ref[k] for t in timeunit for i in project for j in activity for k in resourcetype)
model.addConstrs((er[t,i,j,k] == 0) >> (ru[t,i,j,k] == 0) for t in timeunit for i in project for j in activity for k in resourcetype)

#4. it can not be used more resources than available of every resource type in each period for activities of all projects!! (Korrekt)
model.addConstrs(sum(ru[t,i,j,k] for i in project for j in activity) <= ra[t][k] for t in timeunit for k in resourcetype)

#5. costs due to using resources cannot be more than 20000! (Korrekt)
#model.addConstrs(sum(er[t,i,j,k] * ref[k] * rn[i][j] * rc[k] for t in timeunit for i in project for j in activity for k in resourcetype) <= 20000 for t in timeunit)

#6. every project can only execute at maximum two activities at the same time in every time unit!! (Korrekt)
model.addConstrs(sum(er[t,i,j,k] for j in activity for k in resourcetype) <= 2 for t in timeunit for i in project) 

#7. at least one activity of all the projects has to be executed in every time unit!! (Korrekt)
#model.addConstrs(sum(er[t,i,j,k] for i in project for j in activity for k in resourcetype) >= 1 for t in timeunit)

#8. at maximum four activities of all the projects can be executed simultaneously in every time unit!! (Korrekt)
model.addConstrs(sum(er[t,i,j,k] for i in project for j in activity for k in resourcetype) <=4  for t in timeunit)          

#9. the amount of used resource units of all projects of all activities per timeunit per resource type are equal to the summed number of used resource units of every project and every activity for each time unit and each resourcetype: (Korrekt)
model.addConstrs(sum(ru[t,i,j,k] for i in project for j in activity) == rutk[t,k] for t in timeunit for k in resourcetype)

#10. the amount of used resource units of all projects of all activities of all resourcetypes per timeunit: (Korrekt)
model.addConstrs(sum(rutk[t,k] for k in resourcetype) == rut[t] for t in timeunit)

#11. the amount of per project used resources (summed over the resourcetypes and activities of each project): (Korrekt)
model.addConstrs(sum(ru[t,i,j,k] for j in activity for k in resourcetype) == ruti[t,i] for t in timeunit for i in project)

#11 pnr: decision variable (binary); is project i running in t? (=are resources used by project i to execute aktivities in t?): pnr=1 if the amount of used resources by the project in that timeunit is = 0!, else npr=0 for the project in that timeunit! (Korrekt)
model.addConstrs((pnr[t,i] == 1) >> (ruti[t,i] == 0) for t in timeunit for i in project)
model.addConstrs((pnr[t,i] == 0) >> (ruti[t,i] >= 1) for t in timeunit for i in project)

#12. the 2nd activity can be executed for the first time from the timeact2's time unit: (Korrekt)
model.addConstrs(sum(er[t,i,1,k] for t in timeact2) == 0 for k in resourcetype for i in project)

#13. the 3rd activity can be executed for the first time from the timeact3's time unit: (korrekt)
model.addConstrs(sum(er[t,i,2,k] for t in timeact3) == 0 for k in resourcetype for i in project)

#14. the 4th activity can be executed for the first time from the timeact4's time unit: (korrekt)
model.addConstrs(sum(er[t,i,3,k] for t in timeact4) == 0 for k in resourcetype for i in project)

#15. in the 1st time unit, the first activity of every project has to be executed!! (Korrekt)
model.addConstrs(sum(er[0,i,0,k] for k in resourcetype) == 1 for i in project)   
#model.addConstrs(sum(er[1,i,0,k] for k in resourcetype) == 1 for i in project)       

#16. the first acitivity of every prióject has to be finished within tne first timeact1's time units! (Korrekt)
model.addConstrs(sum(er[t,i,0,k] for t in timeact1 for k in resourcetype) == du[i][0] for i in project)

#17. at least a defined number of pauses np=1 has to be done! pause means: every project doesn't execute any activity!!
#...


#7: run the optimization:

model.optimize()

#8: 

#Lösung ausgeben lassen:
if model.status == GRB.OPTIMAL:    
    print("Die optimale Verteilung der durchzuführenden Aktivitäten ergibt Multiprojektdurchführungskosten von", model.objVal ,"Euro.")    
    
model.getVars()
for t in timeunit:
    for i in project:
        for j in activity:
            for k in resourcetype:
                if (er[t,i,j,k].x == 0):                 
                    print("period: %s project: %s activity: %s resource: %s" % (t,i,j,k))
                    
                    
                    
                        
else:
    print(model.status)
    
#check: resourc   

# 8. TO DO's print: er[k,i,j,t] for all projects, aktivities, time periods and resource types!! 