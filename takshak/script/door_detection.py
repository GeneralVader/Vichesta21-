#!/usr/bin/env python

import rospy
import cv2
import sys
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PointStamped
from cv_bridge import CvBridge, CvBridgeError
import message_filters
import tf
import numpy as np

class door_detection:
    def __init__(self):
        self.bridge = CvBridge()
        self.sub1 = message_filters.Subscriber('/camera/depth/image_rect_raw',Image)
        self.sub2 = message_filters.Subscriber('/odom',Odometry)
        self.sub3 = message_filters.Subscriber('/camera/color/image_raw',Image)
        self.ts = message_filters.TimeSynchronizer([self.sub1,self.sub2,self.sub3],10)
        self.ts.registerCallback(self.callback)
        self.listener = tf.TransformListener()
    def callback(self,depth_data,odom_data,img_data):
        try:
            depth_img = self.bridge.imgmsg_to_cv2(depth_data,"passthrough")
            color_img = self.bridge.imgmsg_to_cv2(img_data,"bgr8")
            color_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
        except CvBridgeError as e:
            print(e)
        point = odom_data.pose.pose.position
        x = point.x
        y = point.y
        orient = odom_data.pose.pose.orientation
        (roll,pitch,yaw) = tf.transformations.euler_from_quaternion([orient.x,orient.y,orient.z,orient.w])
        if (y > -1.25) and (y < -0.70) and (x > -0.1) and (x < 1.2) and (yaw > 0.1) and (yaw < 0.3):
                print('detecting')
                for i in range(5):
                    colors = rospy.get_param('aruco_id_' + str(i))
                    red, green, blue = colors['r'], colors['g'], colors['b']
                    ((cx1,cy1),(cx2,cy2)) = self.segment(color_img,red,green,blue)
                    (odom_x1,odom_y1,odom_z1) = self.cam_to_odom(depth_img,cx1,cy1)
                    (odom_x2,odom_y2,odom_z2) = self.cam_to_odom(depth_img,cx2,cy2)
                    odom_x = float((odom_x1 + odom_x2)/2)
                    odom_y = float((odom_y1 + odom_y2)/2)
                    odom_z = float((odom_z1 + odom_z2)/2)
                    rospy.set_param('door_id_'+str(i), {'x': odom_x, 'y': odom_y, 'z': odom_z}) 
        #cv2.imshow('win',color_img)
        #cv2.waitKey(3)

    def segment(self,color_img,red,green,blue):
        low = np.array([red-10,green-10,blue-10])
        high = np.array([red+10,green+10,blue+10])
        mask = cv2.inRange(color_img,low,high)
        contours, heirarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        centre = list()
        for i in range(2):
            x_sum , y_sum = 0,0
            for cord in contours[i]:
                x_sum += cord[0][0]
                y_sum += cord[0][1]
            x_sum /= contours[i].shape[0]
            y_sum /= contours[i].shape[0]
            #centre[0] += int(x_sum/2)
            #centre[1] += int(y_sum/2)
            centre.append(tuple([int(x_sum), int(y_sum)]))
        #cv2.imshow('segment',mask)
        #cv2.waitKey(3)
        return tuple(centre)

    def cam_to_odom(self,depth_image,cx1,cy1):
        Z = depth_image[cy1,cx1]
        X = Z*(cx1 - 320.5)/320.255
        Y = Z*(cy1 - 240.5)/320.255
        now = rospy.Time.now()
        self.listener.waitForTransform('camera_depth_frame','odom',now,rospy.Duration(4.0))
        msg = PointStamped()
        msg.header.frame_id = "camera_depth_frame"
        msg.point.x = X
        msg.point.y = Y
        msg.point.z = Z
        ret_msg = self.listener.transformPoint('odom', msg)
        #(trans, rot) = self.listener.lookupTransform('camera_depth_frame','odom',now)
        #print(X,Y,Z)
        #print(ret_msg)
        #print('\n\n')
        odom_x = ret_msg.point.x
        odom_y = ret_msg.point.y
        odom_z = ret_msg.point.z
        return (odom_x,odom_y,odom_z)

def main(args):
    rospy.init_node("door_detector", anonymous=True)
    dd = door_detection()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shutting down")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
