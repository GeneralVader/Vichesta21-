#!/usr/bin/env python2.7

from geometry_msgs.msg import PoseStamped
import rospy
import cv2
import sys
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge, CvBridgeError
import message_filters
import tf




class image_converter:
    def __init__(self,k):
        self.bridge = CvBridge()
        self.sub1 = message_filters.Subscriber("/camera/color/image_raw",Image)
        self.sub2 = message_filters.Subscriber("/odom",Odometry)
        self.ts = message_filters.TimeSynchronizer([self.sub1,self.sub2],10)
        self.ts.registerCallback(self.callback)
        self.clear = k

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
 
                cv2.imshow("win", img)
                cv2.waitKey(3)
            
        print('\n\nposition = ' + str([x_cord,y_cord]) + '\n\norientation = ' + str([roll,pitch,yaw]))




def goal_point(pos,ori):
    goal_publisher = rospy.Publisher("move_base_simple/goal", PoseStamped, queue_size=5)

    goal = PoseStamped()

    goal.header.seq = 1
    goal.header.stamp = rospy.Time.now()
    goal.header.frame_id = "map"

    goal.pose.position.x = pos[0]
    goal.pose.position.y = pos[1]
    goal.pose.position.z = pos[2]

    goal.pose.orientation.x = ori[0]
    goal.pose.orientation.y = ori[1]
    goal.pose.orientation.z = ori[2]
    goal.pose.orientation.w = ori[3]
    rospy.sleep(1)

    goal_publisher.publish(goal)

point1=[[-10,-4,0],[0,0,0.6051864, 0.7960838 ]]
point2=[[0.6,-1,0],[0, 0, 0.0998334, 0.9950042 ]]


def main(args):
    rospy.init_node("image_converter")

    goal_point(point1[0],point1[1])
    ic=image_converter(0)
    goal_point(point2[0],point2[1])


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shutting down")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
