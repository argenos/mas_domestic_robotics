cmake_minimum_required(VERSION 2.8.3)
project(mdr_knowledge_base)

find_package(catkin REQUIRED COMPONENTS
  rosplan_knowledge_msgs
  rospy
  roslint
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

roslint_python()
