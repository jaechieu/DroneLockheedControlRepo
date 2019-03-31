#!/usr/bin/env python

# Import required Python code.
import roslib
import rospy
import sys
import message_filters

from rospy import Time
from mav_msgs.msg import RateThrust
from sensor_msgs.msg import Range
from std_msgs.msg import Float64

class autonomous():
    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        self.beginning_time = rospy.get_time()
        self.idle_thrust = float(9.81)

        self.ratethrust_z_sub = message_filters.Subscriber("/rateThrustZ/control_effort", Float64)
        self.ratethrust_roll_sub = message_filters.Subscriber("/rateThrustPitch/control_effort", Float64)
        self.ratethrust_pitch_sub = message_filters.Subscriber("/rateThrustRoll/control_effort", Float64)
        self.ratethrust_yaw_sub = message_filters.Subscriber("/rateThrustYaw/control_effort", Float64)
        self.ratethrust_height_sub = message_filters.Subscriber("/rateThrustYaw/control_effort", Float64)

        self.pub_vel = rospy.Publisher('output/rateThrust', RateThrust, queue_size=2)

        ts = message_filters.ApproximateTimeSynchronizer([self.ratethrust_height_sub, self.ratethrust_z_sub, self.ratethrust_roll_sub, self.ratethrust_pitch_sub, self.ratethrust_yaw_sub], 10, 0.1, allow_headerless=True)
        ts.registerCallback(self.callback)

    def callback(self,range,pid_z,pid_roll,pid_pitch,pid_yaw):
        if range.range >= -1.0:
            msg = RateThrust()
            msg.header.frame_id = "uav/imu"
            msg.header.stamp = Time.now()
            msg.thrust.z = self.idle_thrust + 1;
            msg.angular_rates.x = 0
            msg.angular_rates.y = 0
            msg.angular_rates.z = 0

            self.pub_vel.publish(msg)
        else:
            msg = RateThrust()
            msg.header.frame_id = "uav/imu"
            msg.header.stamp = Time.now()
            msg.thrust.z = pid_z.data
            msg.angular_rates.x = pid_roll.data
            msg.angular_rates.y = pid_pitch.data
            msg.angular_rates.z = pid_yaw.data

            self.pub_vel.publish(msg)

if __name__ == '__main__':
    rospy.init_node('autonomous_control')

    try:
        autonomousNode = autonomous()
        rate = rospy.Rate(20)

        while not rospy.is_shutdown():
            #autonomousNode.ts.registerCallback()
            rate.sleep()
    except rospy.ROSInterruptException: pass
