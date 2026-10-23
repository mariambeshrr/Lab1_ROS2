import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from lab1_interfaces.action import GoToPose
from lab1_interfaces.msg import TargetPose
from lab1_interfaces.srv import SetSpeedLimits


class GoToPoseServer(Node):
    POS_TOL = 0.05          # position tolerance
    YAW_TOL = 0.02          # final heading tolerance (rad)
    HEADING_THRESHOLD = 0.2 # turn in place if heading error is bigger (rad)
    K_LIN = 1.5             # linear gain
    K_ANG = 6.0             # angular gain
    LOOP_DT = 0.02          # 50 Hz
    WORLD_MIN, WORLD_MAX = 0.0, 11.0

    def __init__(self):
        super().__init__('go_to_pose_server')

        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('max_angular_speed', 2.0)
        self.add_on_set_parameters_callback(self.validate_params)
        self.create_service(SetSpeedLimits, 'set_speed_limits', self.set_speed_limits_cb)

        cb_group = ReentrantCallbackGroup()
        self.pose = None
        self.busy = False

        self.create_subscription(Pose, '/turtle1/pose', self.pose_cb, 10, callback_group=cb_group)
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.action_server = ActionServer(
            self, GoToPose, 'go_to_pose',
            execute_callback=self.execute_cb,
            goal_callback=self.goal_cb,
            cancel_callback=self.cancel_cb,
            callback_group=cb_group)

        self.get_logger().info('go_to_pose_server ready')

    def validate_params(self, params):
        for p in params:
            if p.name in ('max_linear_speed', 'max_angular_speed'):
                if p.type_ != Parameter.Type.DOUBLE or p.value <= 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason=f'{p.name} must be a positive float')
        return SetParametersResult(successful=True)

    def set_speed_limits_cb(self, request, response):
        result = self.set_parameters_atomically([
            Parameter('max_linear_speed', Parameter.Type.DOUBLE,
                      request.max_linear_speed),
            Parameter('max_angular_speed', Parameter.Type.DOUBLE,
                      request.max_angular_speed),
        ])
        response.success = result.successful
        response.message = ('Speed limits updated' if result.successful
                            else result.reason)
        self.get_logger().info(f'set_speed_limits: {response.message}')
        return response

    def pose_cb(self, msg):
        self.pose = msg

    def stop(self):
        self.cmd_pub.publish(Twist())

    def goal_cb(self, goal_request):
        t = goal_request.target
        if self.busy:
            self.get_logger().warn('Rejected: already executing a goal')
            return GoalResponse.REJECT
        if not (self.WORLD_MIN < t.x < self.WORLD_MAX and
                self.WORLD_MIN < t.y < self.WORLD_MAX):
            self.get_logger().warn(f'Rejected: ({t.x}, {t.y}) is outside the window')
            return GoalResponse.REJECT
        self.busy = True
        return GoalResponse.ACCEPT

    def cancel_cb(self, goal_handle):
        return CancelResponse.ACCEPT

    def execute_cb(self, goal_handle):
        try:
            return self.run_goal(goal_handle)
        finally:
            self.stop()
            self.busy = False

    def run_goal(self, goal_handle):
        target = goal_handle.request.target
        self.get_logger().info(
            f'Goal received: x={target.x:.2f}, y={target.y:.2f}, yaw={target.yaw:.2f}')

        while self.pose is None and rclpy.ok():
            self.get_logger().info('Waiting for pose...', throttle_duration_sec=2.0)
            time.sleep(0.1)

        feedback = GoToPose.Feedback()
        phase = 'drive'

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return self.make_result(False)

            # Read limits every iteration so changes apply live
            max_v = self.get_parameter('max_linear_speed').value
            max_w = self.get_parameter('max_angular_speed').value

            dx = target.x - self.pose.x
            dy = target.y - self.pose.y
            dist = math.hypot(dx, dy)
            cmd = Twist()

            if phase == 'drive':
                if dist < self.POS_TOL:
                    phase = 'rotate'
                    continue
                raw_err = math.atan2(dy, dx) - self.pose.theta
                angle_err = math.atan2(math.sin(raw_err), math.cos(raw_err))  # wrap to [-pi, pi]
                if abs(angle_err) > self.HEADING_THRESHOLD:
                    cmd.angular.z = max(-max_w, min(max_w, self.K_ANG * angle_err))
                else:
                    cmd.linear.x = max(-max_v, min(max_v, self.K_LIN * dist))
                    cmd.angular.z = max(-max_w, min(max_w, self.K_ANG * angle_err))
            else:  # rotate to final yaw
                raw_err = target.yaw - self.pose.theta
                angle_err = math.atan2(math.sin(raw_err), math.cos(raw_err))  # wrap to [-pi, pi]
                if abs(angle_err) < self.YAW_TOL:
                    break
                cmd.angular.z = max(-max_w, min(max_w, self.K_ANG * angle_err))

            self.cmd_pub.publish(cmd)
            feedback.distance_remaining = dist
            feedback.angle_error = angle_err
            goal_handle.publish_feedback(feedback)
            time.sleep(self.LOOP_DT)

        self.stop()
        goal_handle.succeed()
        self.get_logger().info(
            f'Reached: x={self.pose.x:.3f}, y={self.pose.y:.3f}, '
            f'theta={self.pose.theta:.3f}')
        return self.make_result(True)

    def make_result(self, success):
        result = GoToPose.Result()
        result.success = success
        if self.pose is not None:
            result.final_pose = TargetPose(
                x=float(self.pose.x), y=float(self.pose.y),
                yaw=float(self.pose.theta))
        return result


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()