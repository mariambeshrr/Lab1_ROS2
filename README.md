# Lab1_ROS2

## Team Members:

Mariam Beshr -- 9542

Shahd Taha -- 9374

Nour Tamer -- 9286

## Project Overview

This project implements a modular ROS 2 control system for the turtlesim simulator. It demonstrates the use of custom interfaces (messages, actions, services), multi-threaded action servers, dynamic parameter re-configuration, and high-level behavior composition (drawing a square by chaining pose actions).

## Package Descriptions

### 1. lab1_interfaces
  **Describtion:** Contains custom ROS 2 interface definitions required across the system, including:
    **Custom Message** (TargetPose.msg): Holds target coordinates $(x, y, \text{yaw})$.
    **Custom Action** (GoToPose.action & DrawSquare.action): Manages navigation to a specific pose and high-level square drawing behaviors.
    **Custom Service** (SetSpeedLimits.srv): Dynamic speed limit adjustment interface.

### 2. lab1_control:
 **Description:** Contains core algorithmic nodes and servers for turtle control:
    **go_to_pose_server:** Proportional feedback controller that drives the turtle to a target $(x, y, \text{yaw})$ with live speed parameter reading and collision/window safety checks.
    **reset_server:** Clears the screen and teleports the turtle back to the center origin without drawing trailing pen lines.
    **square_server:** Coordinates the go_to_pose action and reset_server to cleanly draw a square of a given side length.

### 3. lab1_bringup
  **Description:** System integration package containing launch files and parameter configuration files (params.yaml) to start turtlesim and all control nodes simultaneously.

## 🛠️ Installation & Build Steps

1. Copy your package folders (`lab1_interfaces`, `lab1_control`, and `lab1_bringup`) into the `src` directory of your ROS 2 workspace (e.g., `~/ros2_ws/src/`).
2. Open your terminal, navigate to your workspace root, and build the packages using `colcon`:
   ```bash
   git clone https://github.com/mariambeshrr/Lab1_ROS2.git
   cd Lab1_ROS2
   mkdir src
   mv lab1_interfaces lab1_control lab1_bringup src/
   colcon build 
   source install/setup.bash

## How to Run

Start the complete system using the launch file (this starts turtlesim, parameter configs, and all control servers):
```bash
   ros2 launch lab1_bringup lab1.launch.py
```

To open a demo automatic command use:
```bash
   ros2 launch lab1_bringup square.launch.py
```
This launches a a square of side length 3 after a few seconds of launching.

### Commands for Actions, Services, and Nodes

#### 1. Go To Pose Action (/go_to_pose)
Sends the turtle to a specific coordinate and orientation:
```bash
   ros2 action send_goal /go_to_pose lab1_interfaces/action/GoToPose "{target: {x: 8.0, y: 8.0, yaw: 1.57}}" --feedback
```

#### 2. Draw Square Action (/draw_square)
Triggers the turtle to reset and draw a square of a specified side length (e.g., 3.0 meters):
```bash
   ros2 action send_goal /draw_square lab1_interfaces/action/DrawSquare "{side_length: 3.0}" --feedback
```

#### 3. Reset Service (/reset_turtle)
Clears the canvas and teleports the turtle back to the center position $(5.54, 5.54)$ without drawing a connecting line:
```bash
   ros2 service call /reset_turtle std_srvs/srv/Trigger
```

#### 4. Speed Limits Service (/set_speed_limits)
Dynamically updates the maximum linear and angular speed parameters during runtime:
```bash
   ros2 service call /set_speed_limits lab1_interfaces/srv/SetSpeedLimits "{max_linear_speed: 1.5, max_angular_speed: 1.5}"
```

#### 5. ROS 2 Parameters Management
  ##### List parameters:
  ```bash
     ros2 param list /go_to_pose_server
```
  ##### Get a parameter value:
     ros2 param get /go_to_pose_server max_linear_speed
  ##### Set a parameter value directly:
     ros2 param set /go_to_pose_server max_linear_speed 1.0
     
    
