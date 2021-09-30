#!/usr/bin/env python
import rospy
import sys
import roslaunch
from subprocess import Popen  
import subprocess
from nav_msgs.msg import Odometry
import tf
import os
# def callback(msg):
#     # while True:
#     global x,y,orient
#     x=msg.pose.pose.position.x
#     y=msg.pose.pose.position.y
#     orient = msg.pose.pose.orientation
#     (roll,pitch,yaw) = tf.transformations.euler_from_quaternion([orient.x,orient.y,orient.z,orient.w])
#     # if (x>6.3) and (y>5.0) :
#     #     break


def main(args):
    rospy.init_node("controller")

    # odom_sub = rospy.Subscriber('/odom', Odometry,callback)
    # print(odom_sub)
    # for i in range(50):
    #     print(1)

    #rospy.set_param('goal_point',[[-9.65,-2.7,0],[0,0,0.6051864,0.7960838]])
    rospy.set_param('aruco',0)
    rospy.set_param('gate_open',0)
    
    #aruco=subprocess.Popen(["rosrun", "takshak", "aruco_detector.py"])
    while rospy.get_param('aruco') == 0:
        rospy.sleep(0.005)
    #aruco.kill()
    rospy.set_param('goal_point',[[1.4221,-1,0],[ 0, 0, 0.122839, 0.9924266 ]])
    
    
    rospy.set_param('doors',0)
    door=subprocess.Popen(["rosrun", "takshak", "door_detection.py"])
    while rospy.get_param('doors') == 0:
        rospy.sleep(0.005)
    door.kill()



    rospy.set_param('goal_point',[[6.5,6.5,0],[ 0, 0, 0.3662725, 0.9305076 ]])
    rospy.set_param('map_down',0)
    while rospy.get_param('map_down')==0 :
        rospy.sleep(0.1)
    for i in range(50):
        print(1)
    # if (x>6.3) and (y>5.0) :
    path= os.path.abspath("map.pgm")
    print(path)
    mapp=subprocess.Popen(["rosrun", "map_server", "map_saver"])
    rospy.sleep(2)
    mapp.kill()
    rospy.sleep(0.2)

    counting=subprocess.Popen(["rosrun", "takshak", "balls.py"])


    while rospy.get_param('gate_open')==0 :
        rospy.sleep(0.1)
    
    goal_1 =rospy.get_param('gate')
    rospy.set_param('goal_point',goal_1)

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shutting down")


if __name__ == '__main__':
    main(sys.argv)
