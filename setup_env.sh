#!/usr/bin/env bash
# Environment setup for SANDO ROS 2 Lyrical Workspace

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Reset ROS overlay and library paths so only this workspace is active
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH 2>/dev/null

if [ -f "/opt/ros/lyrical/setup.bash" ]; then
    source /opt/ros/lyrical/setup.bash
fi

WS_INSTALL="${SCRIPT_DIR}/install/setup.bash"
if [ -f "$WS_INSTALL" ]; then
    source "$WS_INSTALL"
fi

export GUROBI_HOME="/opt/gurobi1103/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${GUROBI_HOME}/lib:${LD_LIBRARY_PATH}"
export GRB_LICENSE_FILE="${HOME}/gurobi.lic"
