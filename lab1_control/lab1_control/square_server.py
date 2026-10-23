#!/usr/bin/env python3
import time
import rclpy
from rclpy.action import ActionServer, ActionClient
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup   
from rclpy.executors import MultiThreadedExecutor          
from std_srvs.srv import Trigger                           
from lab1_interfaces.action import DrawSquare, GoToPose
from lab1_interfaces.msg import TargetPose

class SquareActionServer(Node):
    def __init__(self):
        super().__init__('square_action_server')
        cb_group = ReentrantCallbackGroup()                
        self._action_server = ActionServer(
            self, DrawSquare, 'draw_square', self.execute_callback,
            callback_group=cb_group
        )
        self._goto_client = ActionClient(self, GoToPose, 'go_to_pose', 
                                         callback_group=cb_group)
        self.reset_client = self.create_client(Trigger, '/reset_turtle',
                                               callback_group=cb_group)
        self.get_logger().info('Square Action Server Ready')

    def execute_callback(self, goal_handle):
        side_length = goal_handle.request.side_length
        if side_length <= 0: #in case an invalid value was entered
            side_length = 3.0

        feedback_msg = DrawSquare.Feedback()
        result = DrawSquare.Result()

        # Reset before drawing
        if not self.reset_client.wait_for_service(timeout_sec=2.0):  
            goal_handle.abort()
            result.success = False
            result.message = 'reset_turtle service not available.'
            return result
        reset_future = self.reset_client.call_async(Trigger.Request())
        while not reset_future.done():                     
            time.sleep(0.01)
        if not reset_future.result().success:              
            goal_handle.abort()
            result.success = False
            result.message = 'Reset failed: ' + reset_future.result().message
            return result

        start_x, start_y = 5.544445, 5.544445              
        corners = [
            (start_x + side_length, start_y, 0.0),
            (start_x + side_length, start_y + side_length, 1.5708),
            (start_x, start_y + side_length, 3.14159),
            (start_x, start_y, -1.5708)
        ]

        for i, (x, y, yaw) in enumerate(corners):
            feedback_msg.current_side = i + 1
            feedback_msg.current_target = TargetPose(x=x, y=y, yaw=yaw)
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Side {i + 1}/4: goToPose goal -> ({x:.2f}, {y:.2f}, {yaw:.2f})')

            if not self._goto_client.wait_for_server(timeout_sec=5.0):
                goal_handle.abort()
                result.success = False
                result.message = 'go_to_pose action server not available.'
                return result

            goal_msg = GoToPose.Goal()
            goal_msg.target = TargetPose(x=x, y=y, yaw=yaw)   

            send_goal_future = self._goto_client.send_goal_async(goal_msg)
            while not send_goal_future.done():            
                time.sleep(0.01)

            goal_handle_pose = send_goal_future.result()
            if not goal_handle_pose.accepted:             
                goal_handle.abort()
                result.success = False
                result.message = f'goToPose rejected side {i + 1} (target outside window?).'
                return result

            get_result_future = goal_handle_pose.get_result_async()
            while not get_result_future.done():            
                time.sleep(0.05)

            if not get_result_future.result().result.success:   
                goal_handle.abort()
                result.success = False
                result.message = f'goToPose failed on side {i + 1}.'
                return result

        goal_handle.succeed()
        result.success = True
        result.message = 'Square drawn successfully.'
        return result

def main(args=None):
    rclpy.init(args=args)
    node = SquareActionServer()
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