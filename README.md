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
   cd ~/ros2_ws
   colcon build --packages-select lab1_interfaces lab1_control lab1_bringup
