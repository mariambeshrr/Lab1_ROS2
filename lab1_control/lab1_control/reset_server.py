#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Empty, Trigger
from turtlesim.srv import SetPen, TeleportAbsolute


class ResetServer(Node):
    def __init__(self):
        super().__init__('reset_server')
        group = ReentrantCallbackGroup()

        self.clear = self.create_client(Empty, '/clear', callback_group=group)
        self.pen = self.create_client(SetPen, '/turtle1/set_pen', callback_group=group)
        self.teleport = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute', callback_group=group)
        self.create_service(Trigger, 'reset_turtle', self.reset, callback_group=group)

        self.get_logger().info('reset server ready')

    def reset(self, request, response):
        calls = [
            (self.pen, SetPen.Request(r=179, g=184, b=255, width=3, off=1)),  # pen up, no line
            (self.teleport, TeleportAbsolute.Request(x=5.544445, y=5.544445, theta=0.0)),
            (self.clear, Empty.Request()),
            (self.pen, SetPen.Request(r=179, g=184, b=255, width=3, off=0)),  # pen back down
        ]
        for client, req in calls:
            client.wait_for_service()
            future = client.call_async(req)
            while not future.done():
                time.sleep(0.01)

        response.success = True
        response.message = 'reset done'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ResetServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()