#!/usr/bin/env python2.7

import rospy
import cv2
import sys
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge, CvBridgeError
import message_filters
import tf

class image_converter:
    def __init__(self):
        self.bridge = CvBridge()
        self.sub1 = message_filters.Subscriber("/camera/color/image_raw",Image)
        self.sub2 = message_filters.Subscriber("/odom",Odometry)
        self.ts = message_filters.TimeSynchronizer([self.sub1,self.sub2],10)
        self.ts.registerCallback(self.callback)

    def callback(self,img_data,odom_data):
        try:
            img = self.bridge.imgmsg_to_cv2(img_data,"bgr8")
        except CvBridgeError as e:
            print(e)
        print(img.shape)
        point = odom_data.pose.pose.position
        x_cord = point.x
        y_cord = point.y
        orient = odom_data.pose.pose.orientation
        (roll,pitch,yaw) = tf.transformations.euler_from_quaternion([orient.x,orient.y,orient.z,orient.w])
        if (x_cord < -9) and (x_cord > -11) and (yaw > 1.0) and (yaw < 1.7) and (y_cord < -3) and (y_cord > -5) :
            print("detecting aruco markers")
            arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_250)
            arucoParams = cv2.aruco.DetectorParameters_create()
            (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict, parameters=arucoParams)
            if len(ids)==5:
                centres = dict()
                for i in range(5):
                    x_sum ,y_sum = 0,0
                    for j in range(4):
                        x_sum += int(corners[i][0][j][0]/4)
                        y_sum += int(corners[i][0][j][1]/4)
                    centres[ids[i][0]] = [x_sum,y_sum]
                    #img = cv2.circle(img, (x_sum,y_sum), radius=5, color=(0,0,255), thickness=-1)
                    #img = cv2.circle(img, (x_sum,y_sum-35), radius = 5, color=(255,255,255), thickness=-1)
                    #img = cv2.putText(img, str(ids[i][0]), (x_sum,y_sum-35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                print(centres)
                for i in range(5):
                    x = centres[i][0]
                    y = centres[i][1]
                    b = int(img[y-35,x,0])
                    g = int(img[y-35,x,1])
                    r = int(img[y-35,x,2])
                    rospy.set_param('aruco_id_'+str(ids[i][0]),{'r': r, 'g': g, 'b': b})
                    rospy.set_param('aruco',1)
            cv2.imshow("win", img)
            cv2.waitKey(3)
        print('\n\nposition = ' + str([x_cord,y_cord]) + '\n\norientation = ' + str([roll,pitch,yaw]))


def main(args):
    ic = image_converter()
    rospy.init_node("image_converter", anonymous=True)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shutting down")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)

