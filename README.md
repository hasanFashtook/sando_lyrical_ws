# SANDO ROS 2 Lyrical Workspace (`sando_lyrical_ws`)

Port of the **SANDO** (Safe Autonomous Trajectory Planning for Dynamic Unknown Environments) drone navigation framework to **ROS 2 Lyrical Luth** on **Ubuntu 26.04 LTS (Resolute Raccoon)** with **GCC 15.2** and **CMake 4.2+**.

---

## 1. Architecture & Package Inventory

The workspace is fully self-contained and comprises **23 packages** organized into five sub-trees:

| Package Sub-tree | Packages | Description |
| :--- | :--- | :--- |
| **`src/sando`** | `sando` | Main SANDO trajectory planner node, HGP manager, corridor generator, benchmark tools, and `fake_sim`. |
| **`src/dynus_interfaces`** | `dynus_interfaces` | Core ROS 2 custom message and service definitions (`Goal`, `State`, `DynTraj`). |
| **`src/DecompROS2`** | `decomp_util`, `decomp_ros_msgs`, `decomp_rviz_plugins`, `decomp_test_node` | Safe flight corridor (SFC) convex polyhedron decomposition library and RViz visualization plugins. |
| **`src/acl-mapping`** | `fla_interfaces`, `fla_utils`, `global_mapper`, `global_mapper_ros` | Volumetric voxel occupancy mapping and map processing services. |
| **`src/uav_simulator`** | `so3_control`, `so3_quadrotor_simulator`, `fake_drone`, `local_sensing`, `map_generator`, `mockamap`, `multi_map_server`, `odom_visualization`, `poscmd_2_odom`, `pose_utils`, `quadrotor_msgs`, `uav_utils`, `waypoint_generator` | Lightweight UAV flight dynamics, sensor simulation, and multi-map tools. |

---

## 2. Key Porting Highlights & Compatibility Principles

1. **Zero Solver Rewrite / 100% Byte-for-Byte Solver Integrity**:
   - The Gurobi optimization solver (`src/sando/gurobi_solver.cpp` and `include/sando/gurobi_solver.hpp`) is **100% byte-for-byte identical** to the upstream reference repository at `/home/hasan-fashtouk/code/sando`.
   - Verified via `diff -u` and identical MD5 hashes:
     - `gurobi_solver.cpp`: `15bbb5ab9c4d2a023f4cd88cb8fdf185`
     - `gurobi_solver.hpp`: `fa5e2a2d8668a3c2de53b26f86fe5112`
2. **Upstream Isolation**:
   - The canonical upstream repository at `/home/hasan-fashtouk/code/sando` remains completely untouched and pristine (`git status --porcelain` is empty).
3. **Gazebo Classic Elimination**:
   - Deprecated Gazebo Classic plugins and targets are cleanly isolated behind `BUILD_SIMULATION=OFF`.
   - `fake_sim` was modernized to use `ros_gz_interfaces/srv/SetEntityPose`.
4. **Header & CMake Modernization**:
   - Replaced deprecated `.h` includes (`tf2_eigen`, `tf2_ros`, `message_filters`, `tf2/LinearMath`) with modern `.hpp` headers.
   - Replaced obsolete `ament_target_dependencies` macro with standard modern CMake target linking (`rclcpp::rclcpp`, `${dynus_interfaces_TARGETS}`, etc.).
   - Modernized rosbag2 timestamp field from `time_stamp` to `recv_timestamp`.
   - Exported public include directories in `decomp_rviz_plugins`.

---

## 3. Runtime Gurobi Execution Status

> [!NOTE]
> **Active Gurobi Runtime License**:
> A valid Gurobi license is installed at `/home/hasan-fashtouk/gurobi.lic` (LicenseID `2878908`).
> Runtime trajectory generation, safe flight corridor optimization, and simulation flights with Gurobi are fully active and validated on ROS 2 Lyrical with zero licensing restrictions.

---

## 4. Setup & Build Instructions

### Prerequisites
- Ubuntu 26.04 LTS (Resolute Raccoon)
- ROS 2 Lyrical Luth (`/opt/ros/lyrical`)
- Gurobi 11.0.3 Linux64 SDK installed at `/opt/gurobi1103/linux64` with `libgurobi_c++.a` compiled using host GCC 15.

### Environment Sourcing
Always source `setup_env.sh` prior to building or running workspace tools:

```bash
cd ~/code/sando_lyrical_ws
source setup_env.sh
```

`setup_env.sh` sets:
```bash
export GUROBI_HOME="/opt/gurobi1103/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${GUROBI_HOME}/lib:${LD_LIBRARY_PATH}"
source /opt/ros/lyrical/setup.bash
if [ -f "/home/hasan-fashtouk/code/sando_lyrical_ws/install/setup.bash" ]; then
    source "/home/hasan-fashtouk/code/sando_lyrical_ws/install/setup.bash"
fi
```

### Resource-Efficient Compilation (3 Cores / Low Memory)
To build the workspace without exhausting system memory or starving interactive applications:

```bash
cd ~/code/sando_lyrical_ws
source setup_env.sh

export MAKEFLAGS="-j3"
colcon build \
  --parallel-workers 1 \
  --cmake-args \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SIMULATION=OFF \
    -DCMAKE_BUILD_PARALLEL_LEVEL=3
```

---

## 5. Verification Commands

1. **Verify all packages built successfully**:
   ```bash
   ros2 pkg list | grep -E "sando|decomp|dynus|global_mapper|uav_simulator"
   ```

2. **Verify installed SANDO executables**:
   ```bash
   ls -la install/sando/lib/sando/
   ```
   Expected executables:
   - `sando`
   - `fake_sim`
   - `obstacle_tracker_node`
   - `convert_goal_to_cmd_vel`
   - `convert_odom_to_state`
   - `convert_vicon_to_state`
   - `odom_to_global_state`
   - `corridor_generator_node`
   - `local_traj_benchmark_node`
   - `visualize_local_trajs_node`
   - `temporal_layered_corridor_test_node`
   - `analyze_benchmark`
   - `convert_bag`

3. **Verify Solver Identity**:
   ```bash
   diff -u /home/hasan-fashtouk/code/sando/src/sando/gurobi_solver.cpp src/sando/src/sando/gurobi_solver.cpp
   diff -u /home/hasan-fashtouk/code/sando/include/sando/gurobi_solver.hpp src/sando/include/sando/gurobi_solver.hpp
   ```
   Expected result: Completely empty output (zero difference).

4. **Verify Upstream Pristine State**:
   ```bash
   cd /home/hasan-fashtouk/code/sando && git status --porcelain
   ```
   Expected result: Completely empty output (no untracked, modified, or staged files).

---

## 6. Simulation & Runtime Commands (Parity with `mighty_lyrical_ws`)

All simulation modes run via the unified `run_sim.py` launcher in tmux with full ROS 2 Lyrical and Gurobi environment configuration:

### Interactive Simulation (Click-to-Goal in RViz)
```bash
cd ~/code/sando_lyrical_ws
python3 src/sando/scripts/run_sim.py --mode interactive -s install/setup.bash
```
*Features*: RViz opens automatically with 100 dynamic and static obstacles. Use the RViz **2D Nav Goal** tool to click any goal coordinate in the arena; SANDO optimizes the trajectory with Gurobi and executes collision-free flight to the target.

### Multi-Agent Simulation (Circle Formation Swap)
```bash
cd ~/code/sando_lyrical_ws
python3 src/sando/scripts/run_sim.py --mode multiagent -s install/setup.bash --num-agents 4
```
*Features*: Spawns 4 drones (or up to 10 via `--num-agents 10`) on a circle perimeter. Each drone plans with SANDO, broadcasts on `/trajs`, and performs real-time collision avoidance with opposing drones while swapping circle positions.

### RViz-Only Flight Simulation with Dynamic Obstacles
```bash
cd ~/code/sando_lyrical_ws
python3 src/sando/scripts/run_sim.py --mode rviz-only -s install/setup.bash --goal 50 0 2
```
*Features*: Drone navigates through a dense field of dynamic trefoil obstacles to the target goal `(50, 0, 2)`.

### Gazebo Harmonic Simulation (Modernized for ROS 2 Lyrical)
```bash
# Single-agent simulation in easy_forest (headless Gazebo + RViz2)
python3 src/sando/scripts/run_sim.py --mode gazebo --env easy_forest -s install/setup.bash

# Single-agent simulation with Gazebo Harmonic GUI enabled
python3 src/sando/scripts/run_sim.py --mode gazebo --env easy_forest --gazebo-gui -s install/setup.bash

# Single-agent simulation in ring_forest
python3 src/sando/scripts/run_sim.py --mode gazebo --env ring_forest -s install/setup.bash

# Gazebo Harmonic with dynamic obstacle avoidance
python3 src/sando/scripts/run_sim.py --mode gazebo-dynamic --env easy_forest -s install/setup.bash
```
*Features*:
- Full native integration with **Gazebo Harmonic (Gz Sim)** on ROS 2 Lyrical without legacy `gazebo_ros` or `gazebo_msgs`.
- **GPU LiDAR Sensing**: Simulated Livox mid360 point cloud bridged to `/NX01/mid360_PointCloud2` using `ros_gz_bridge`.
- **Real-time Occupancy Voxel Mapping**: `global_mapper_ros` ingests the LiDAR stream and maintains 3D voxel occupancy grids.
- **Kinematic Pose Teleportation**: Modern `ros_gz_interfaces/srv/SetEntityPose` service updates the UAV model pose in Gazebo at `/world/<world_name>/set_pose`.
- **SDF Worlds**: Includes native Gazebo Harmonic worlds (`empty.sdf`, `easy_forest.sdf`, `medium_forest.sdf`, `hard_forest.sdf`, `ring_forest.sdf`, etc.).

### Standalone Trajectory & Safe Flight Corridor Benchmark
```bash
cd ~/code/sando_lyrical_ws
source setup_env.sh
ros2 run sando temporal_layered_corridor_test_node
```
*Expected*: Layered corridor generation and Gurobi MIQP optimization complete with `worst union violation <= 0` (feasible safe flight).

---

## 7. Simulation Termination & Cleanup (إيقاف المحاكاة بالكامل)

To cleanly and completely terminate all background simulation processes (Gazebo Harmonic, `ros_gz_bridge`, RViz2, SANDO nodes, and tmux sessions), you can use any of the following methods:

### Method 1: Using the helper script (Recommended)
```bash
cd ~/code/sando_lyrical_ws
./stop_sim.sh
```

### Method 2: Using the python launcher `--kill` flag
```bash
cd ~/code/sando_lyrical_ws
python3 src/sando/scripts/run_sim.py --kill
```

### Method 3: Direct terminal one-liner commands
```bash
# 1. Kill the active tmux session
tmux kill-session -t sando_sim

# 2. Terminate Gazebo Harmonic and ROS-Gz Bridge processes
killall -9 ruby 2>/dev/null
pkill -9 -f "gz sim" 2>/dev/null
pkill -9 -f "ros_gz_bridge" 2>/dev/null
pkill -9 -f "parameter_bridge" 2>/dev/null

# 3. Terminate ROS 2 nodes and RViz2
pkill -9 -f "ros2 launch" 2>/dev/null
pkill -9 -x rviz2 2>/dev/null
pkill -9 -x fake_sim 2>/dev/null
pkill -9 -x sando 2>/dev/null
pkill -9 -x dynamic_forest_node 2>/dev/null
pkill -9 -f "global_mapper" 2>/dev/null
pkill -9 -f "obstacle_tracker_node" 2>/dev/null
pkill -9 -f "goal_relay" 2>/dev/null
```



