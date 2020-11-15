#!/usr/bin/env python
import rospy
import sys
import math
import tf
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
###############################
# NEED TO ADD to launch file  # RUN rosrun prrexamples key_publisher.py to get /keys
###############################
key_mapping = { 'a': [0,1], 'd': [0,-1],
                'w': [ 1, 0], 's': [-1,  0],
                'x': [ 0, 0] }
# fill in scan callback
def scan_cb(msg):
   global state
   rangesInFront = msg.ranges[:45] + msg.ranges[314:] # these are the degrees that will detect an object 
   if min(rangesInFront) <= .2:
      state = 'x'
def odometryCb(msg):
    #establishing global variable from callBack to be used else where
    global msgObj
    global getThereDistance
    global x,y,z 
    msgObj = msg.pose.pose.orientation
    getThereDistance = msg.pose.pose.position.x
    zPosition = msgObj.z
    quat = (msgObj.x, msgObj.y, msgObj.z, msgObj.w)
    #create a list of the orientation coordinates 
    roll,pitch,yaw = euler_from_quaternion(quat)   
# it is not necessary to add more code here but it could be useful
def key_cb(msg):
   global state; global last_key_press_time;global linear_component;global angular_component
   state = msg.data
   last_key_press_time = rospy.Time.now()
   if state in key_mapping.keys():
      linear_component , angular_component = key_mapping[state]
# print the state of the robot
def print_state():
   print("---")
   print("STATE: " + state)
   # calculate time since last key stroke
   time_since = rospy.Time.now() - last_key_press_time
   print("SECS SINCE LAST KEY PRESS: " + str(time_since.secs))
#def left():
   #desired = 89 #angle we want to turn towards
   #while getThereDistance >= dersired
#def right():
   #desired = 269 #angle we want to turn towards 
# init node
rospy.init_node('pacman-motion')
# subscribers/publishers
scan_sub = rospy.Subscriber('scan', LaserScan, scan_cb)
# RUN rosrun prrexamples key_publisher.py to get /keys
key_sub = rospy.Subscriber('keys', String, key_cb)
rospy.Subscriber('odom',Odometry,odometryCb)
cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
# start in state halted and grab the current time
state = "x"
last_key_press_time = rospy.Time.now()
# set rate
rate = rospy.Rate(10)
LINEAR_SPEED = .3
ANGULAR_SPEED = .5
linear_component = 0 
angular_component = 0
difference = rospy.Time.now()
stop = True
# Wait for published topics, exit on ^c
while not rospy.is_shutdown():
   # print out the current state and time since last key press
   linear_component,angular_component = key_mapping.get(state,(0,0))
   print_state()
   # publish cmd_vel from here 
   t = Twist()
   t.linear.x = LINEAR_SPEED * linear_component 
   t.angular.z = ANGULAR_SPEED * angular_component 
   # where for example:
   # LINEAR_SPED = 0.2, ANGULAR_SPEED = pi/4
   # velocity_vector = [1,0] for positive linear and no angular movement
   # velocity_vector = [-1, 1] for negative linear and positive angular movement
   # you will need one velocity vector for each state then so 
   # we can then create a dictionary state: movement_vector to hash the current state to get the movement_vector
   # in order to get the zig zag and spiral motion you could you something like this:
   # twist.linear.x = LINEAR_SPEED * linear_component * linear_transform
   # twist.angular.z = ANGULAR_SPEED * angular_component * angular_transform
   # where the [linear_transform, angular_transform] is derived from another source that is based on the clock
   # now you can change the velocity of the robot at every step of the program based on the state and the time
   #do i need to change this order so check something if called first 
   cmd_vel_pub.publish(t)
   # run at 10hz
   rate.sleep()