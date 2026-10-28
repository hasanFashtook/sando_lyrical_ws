#!/usr/bin/env python3
# /* ----------------------------------------------------------------------------
#  * Copyright 2026, Kota Kondo, Aerospace Controls Laboratory
#  * Massachusetts Institute of Technology
#  * All Rights Reserved
#  * Authors: Kota Kondo, et al.
#  * See LICENSE file for the license information
#  * -------------------------------------------------------------------------- */

"""Main SANDO launch: Gazebo Harmonic simulation with ros_gz_bridge, RViz, and dynamic obstacles."""

import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def convert_str_to_bool(s):
    if isinstance(s, bool):
        return s
    return str(s).lower() in ("true", "1", "yes", "on", "t")


def generate_launch_description():
    env_arg = DeclareLaunchArgument(
        "env",
        default_value="easy_forest",
        description="Environment name to determine the Gazebo world file",
    )
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz", default_value="true", description="Flag to enable or disable RViz"
    )
    use_gazebo_gui_arg = DeclareLaunchArgument(
        "use_gazebo_gui",
        default_value="false",
        description="Flag to enable or disable gazebo gui",
    )
    use_dyn_obs_arg = DeclareLaunchArgument(
        "use_dyn_obs",
        default_value="false",
        description="Flag to enable or disable dynamic obstacles",
    )
    world_file_arg = DeclareLaunchArgument(
        "world_file",
        default_value="",
        description="Full path override for world file (bypasses env mapping)",
    )
    rviz_config_arg = DeclareLaunchArgument(
        "rviz_config",
        default_value=os.path.join(
            get_package_share_directory("sando"), "rviz", "sando.rviz"
        ),
        description="Path to RViz config file",
    )

    def launch_setup(context, *args, **kwargs):
        env_value = LaunchConfiguration("env").perform(context)
        world_mapping = {
            "high_res_forest": "big_forest_high_res.sdf",
            "static_uncertainty_test2": "static_uncertainty_test2.sdf",
            "static_uncertainty_test3": "static_uncertainty_test3.sdf",
            "static_uncertainty_test4": "static_uncertainty_test4.sdf",
            "office_faster": "office.sdf",
            "office": "office.sdf",
            "cave_start": "simple_tunnel.sdf",
            "cave_vertical": "simple_tunnel.sdf",
            "cave_person": "simple_tunnel.sdf",
            "forest3": "forest3.sdf",
            "yaw_benchmark": "forest3.sdf",
            "global_planner": "forest3.sdf",
            "multiagent_performance": "forest3.sdf",
            "path_push": "forest3.sdf",
            "ACL_office": "ACL_office.sdf",
            "ground_robot": "ACL_office.sdf",
            "multiagent_testing": "empty.sdf",
            "empty_wo_ground": "empty_wo_ground.sdf",
            "empty": "empty.sdf",
            "hospital": "hospital.sdf",
            "easy_forest": "easy_forest.sdf",
            "easy_high_forest": "easy_high_forest.sdf",
            "medium_forest": "medium_forest.sdf",
            "hard_forest": "hard_forest.sdf",
            "dynamic_forest": "dynamic_forest.sdf",
            "ring_forest": "ring_forest.sdf",
        }

        world_file_override = LaunchConfiguration("world_file").perform(context).strip()
        if world_file_override:
            world_path = world_file_override
            world_name = os.path.splitext(os.path.basename(world_path))[0]
        else:
            world_file = world_mapping.get(env_value, f"{env_value}.sdf")
            world_path = os.path.join(get_package_share_directory("sando"), "worlds", world_file)
            world_name = env_value

        use_rviz = convert_str_to_bool(LaunchConfiguration("use_rviz").perform(context))
        use_dyn_obs = convert_str_to_bool(LaunchConfiguration("use_dyn_obs").perform(context))
        use_gazebo_gui = convert_str_to_bool(LaunchConfiguration("use_gazebo_gui").perform(context))

        # 1. Gazebo Harmonic Launch
        gz_gui_flag = "" if use_gazebo_gui else "-s "
        gz_args = f"{gz_gui_flag}-r {world_path}"
        gz_sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
            ),
            launch_arguments={"gz_args": gz_args, "on_exit_shutdown": "true"}.items(),
        )

        # 2. ros_gz_bridge (Clock, LiDAR PointCloud, and SetEntityPose Service)
        bridge_config_file = os.path.join(
            get_package_share_directory("sando"), "config", "ros_gz_bridge.yaml"
        )
        set_pose_service_arg = (
            f"/world/{world_name}/set_pose@ros_gz_interfaces/srv/SetEntityPose@gz.msgs.Pose@gz.msgs.Boolean"
        )
        ros_gz_bridge_node = Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            name="ros_gz_bridge",
            output="screen",
            arguments=[set_pose_service_arg],
            parameters=[{"config_file": bridge_config_file}],
        )

        # 3. Static Transforms for LiDAR sensor chain
        tf_base_to_livox = Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="static_tf_base_link_to_livox",
            output="screen",
            parameters=[{"use_sim_time": True}],
            arguments=[
                "--x", "0.12", "--y", "0", "--z", "0.26",
                "--roll", "0", "--pitch", "0", "--yaw", "0",
                "--frame-id", "NX01/base_link",
                "--child-frame-id", "NX01/NX01_livox",
            ],
        )
        tf_livox_to_optical = Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="static_tf_livox_to_gz_frame",
            output="screen",
            parameters=[{"use_sim_time": True}],
            arguments=[
                "--frame-id", "NX01/NX01_livox",
                "--child-frame-id", "livox_frame",
            ],
        )

        # 4. RViz2 Visualization
        rviz_config_file = LaunchConfiguration("rviz_config").perform(context)
        rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="log",
            emulate_tty=True,
            arguments=["-d", rviz_config_file, "--ros-args", "--log-level", "error"],
            parameters=[{"use_sim_time": True}],
        )

        # 5. Dynamic Obstacles (Optional)
        dynamic_obstacles_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare("sando"), "launch", "dyn_obstacles.launch.py"])
            ),
            launch_arguments={
                "num_obstacles": "20",
                "publish_rate_hz": "50.0",
                "seed": "0",
                "launch_forest_node": "true",
                "publish_markers": "true",
                "publish_tf": "true",
                "publish_trajs": "true",
                "trajs_topic": "/trajs",
                "use_sim_time": "true",
                "skip_gazebo": "true",
            }.items(),
        )

        nodes_to_start = [gz_sim_launch, ros_gz_bridge_node]
        if use_rviz:
            nodes_to_start.append(rviz_node)
        if use_dyn_obs:
            nodes_to_start.append(dynamic_obstacles_launch)

        return nodes_to_start

    return LaunchDescription(
        [
            env_arg,
            use_rviz_arg,
            use_gazebo_gui_arg,
            use_dyn_obs_arg,
            world_file_arg,
            rviz_config_arg,
            OpaqueFunction(function=launch_setup),
        ]
    )
