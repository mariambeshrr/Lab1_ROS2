#!/usr/bin/env python3
import time
import rclpy
from rclpy.action import ActionServer, ActionClient
from rclpy.node import Node 
from std_srvs.srv import Empty
from lab1_interfaces.action import DrawSquare, GoToPose #this is for the action definitions - names might be edited!!!!!
from lab1_interfaces.msg import TargetPose #same here!!!!!

class SquareActionServer(Node):
    def __init__(self):
        super().__init__('square_action_server')
        self._action_server = ActionServer(
            self, DrawSquare, 'draw_square', self.execute_callback
        )
        self._goto_client = ActionClient(self, GoToPose, 'goto_pose')
        self.reset_client = self.create_client(Empty, '/reset_turtle')
        self.get_logger().info('Square Action Server Ready')

    def execute_callback(self, goal_handle):
        side_length = goal_handle.request.side_length
        if side_length <= 0: #in case an invalid value was entered 
            side_length = 3.0
            
        feedback_msg = DrawSquare.Feedback()
        result = DrawSquare.Result()
        
        # Reset before drawing
        if self.reset_client.wait_for_service(timeout_sec=2.0):
            self.reset_client.call_async(Empty.Request())
            time.sleep(0.5)
            
        start_x, start_y = 5.54, 5.54
        corners = [
            (start_x + side_length, start_y, 0.0),
            (start_x + side_length, start_y + side_length, 1.5708),
            (start_x, start_y + side_length, 3.14159),
            (start_x, start_y, -1.5708)
        ]
        
        for i, (x, y, yaw) in enumerate(corners):
            feedback_msg.current_side = i + 1
            goal_handle.publish_feedback(feedback_msg)
            
            if not self._goto_client.wait_for_server(timeout_sec=5.0):
                goal_handle.abort()
                result.success = False
                return result
                
            goal_msg = GoToPose.Goal()
            goal_msg.target_pose = TargetPose(x=x, y=y, yaw=yaw)
            
            send_goal_future = self._goto_client.send_goal_async(goal_msg)
            rclpy.spin_until_future_complete(self, send_goal_future)
            
            goal_handle_pose = send_goal_future.result()
            get_result_future = goal_handle_pose.get_result_async()
            rclpy.spin_until_future_complete(self, get_result_future)
            
        goal_handle.succeed()
        result.success = True
        result.message = 'Square drawn successfully.'
        return result

def main(args=None):
    rclpy.init(args=args)
    node = SquareActionServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
