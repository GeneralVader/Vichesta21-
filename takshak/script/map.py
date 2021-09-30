#!/usr/bin/env python

# import roslaunch
# import rospy

# rospy.init_node('en_Mapping', anonymous=True)
# uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
# roslaunch.configure_logging(uuid)
# launch = roslaunch.parent.ROSLaunchParent(uuid, ["/home/varad/catkin_ws/src/Vichesta21-/takshak/launch/map.launch"])
# launch.start()
# rospy.loginfo("started")

# rospy.sleep(3)
# # 3 seconds later
# launch.shutdown()

# import roslaunch
# import time

# package = 'map_server'
# executable = 'map_saver'
# node = roslaunch.core.Node(package, executable)

# launch = roslaunch.scriptapi.ROSLaunch()
# launch.start()
# time.sleep(20)

# process = launch.launch(node)
# print process.is_alive()
# process.stop()
from subprocess import Popen  
import subprocess

subprocess.Popen(["rosrun", "map_server", "map_saver"])