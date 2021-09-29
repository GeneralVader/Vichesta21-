#!/usr/bin/env python
import rospy
import sys

def main(args):
    rospy.init_node("controller")
    rospy.set_param('goal_point',[[-9.75,-3.0,0],[0,0,0.6051864,0.7960838]])
    rospy.set_param('aruco',0)
    while rospy.get_param('aruco') == 0:
        rospy.sleep(0.005)
    rospy.set_param('goal_point',[[0.6,-1,0],[0, 0, 0.0998334, 0.9950042 ]])
    

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shutting down")


if __name__ == '__main__':
    main(sys.argv)
