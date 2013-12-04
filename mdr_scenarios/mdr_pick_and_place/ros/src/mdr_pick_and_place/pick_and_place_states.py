#!/usr/bin/python

import rospy
import smach
import smach_ros
import moveit_commander

import std_srvs.srv
import mcr_perception_msgs.msg

from mdr_common_states.common_states import *


class init_manipulator(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['success'])
		self.recover_srv = rospy.ServiceProxy('/arm_controller/lwr_node/recover', std_srvs.srv.Empty)

	def execute(self, userdata):
		rospy.wait_for_service('/arm_controller/lwr_node/recover')
		recover = rospy.ServiceProxy('/arm_controller/lwr_node/recover', std_srvs.srv.Empty)
		try:
			recover()
		except rospy.ServiceException, e:
			print "Service did not process request: %s"%str(e)

		return 'success'

class find_any_known_object_height_based(smach.State):
	def __init__(self):	
		smach.State.__init__(self, outcomes=['success','failed'], output_keys=['grasp_position'])
		self.find_object_srv = rospy.ServiceProxy('/mcr_perception/object_recognition_height_based/get_recognized_objects', mcr_perception_msgs.srv.GetObjectList)
		self.object_recognition_start = rospy.ServiceProxy('/mcr_perception/object_recognition_height_based/start', std_srvs.srv.Empty)
		self.object_recognition_stop = rospy.ServiceProxy('/mcr_perception/object_recognition_height_based/stop', std_srvs.srv.Empty)
		self.arm = moveit_commander.MoveGroupCommander('arm')

	def execute(self, userdata):
		rospy.wait_for_service('/mcr_perception/object_recognition_height_based/start', 30)
		rospy.wait_for_service('/mcr_perception/object_recognition_height_based/stop', 30)
		self.object_recognition_start()
		
		sss.move("head", "back_table", False)
		self.arm.plan("look_at_table")
		self.arm.go()
		sss.move("torso", "extrem_back")
		
		rospy.wait_for_service('/mcr_perception/object_recognition/get_recognized_objects', 30)
		for i in range(20): 
			print "calling /mcr_perception/object_recognition/get_recognized_objects service"
			resp = self.find_object_srv()

			if (len(resp.object_position_list) <= 0):
				print "no graspable objects found"
				rospy.sleep(1)
			else:
				break
				
		if (len(resp.object_position_list) <= 0):
			SAY("I could not find any object.")
			self.arm.plan("folded")
			self.arm.go()
			sss.move("head","front_face",False)
			self.object_recognition_stop()
			return 'failed'

		SAY("I see ")
		for recObject in resp.object_position_list:
			SAY(recObject.name + ", ")

		object_to_grasp = resp.object_position_list.pop()
		userdata.grasp_position = object_to_grasp.position.point
		SAY("I will now grasp the " + object_to_grasp.name)
		self.object_recognition_stop()
		return 'success'