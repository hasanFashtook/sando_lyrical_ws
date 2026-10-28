#!/usr/bin/env bash
# ==============================================================================
# Script to completely terminate SANDO, Gazebo Harmonic, and ROS 2 simulation
# ==============================================================================

echo "Terminating all SANDO, Gazebo, and ROS 2 simulation processes..."

# 1. Kill tmux session
tmux kill-session -t sando_sim 2>/dev/null

# 2. Terminate Gazebo Harmonic and bridge
killall -9 ruby 2>/dev/null
pkill -9 -f "gz sim" 2>/dev/null
pkill -9 -f "ros_gz_bridge" 2>/dev/null
pkill -9 -f "parameter_bridge" 2>/dev/null

# 3. Terminate ROS 2 launchers and nodes
pkill -9 -f "ros2 launch" 2>/dev/null
pkill -9 -x rviz2 2>/dev/null
pkill -9 -x fake_sim 2>/dev/null
pkill -9 -x sando 2>/dev/null
pkill -9 -x dynamic_forest_node 2>/dev/null
pkill -9 -f "global_mapper" 2>/dev/null
pkill -9 -f "obstacle_tracker_node" 2>/dev/null
pkill -9 -f "goal_relay" 2>/dev/null
pkill -9 -f "goal_sender" 2>/dev/null
pkill -9 -f "tmuxp" 2>/dev/null

echo "All simulation processes stopped cleanly."
