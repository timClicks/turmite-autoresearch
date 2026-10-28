# source this before building/running with --features cuda (WSL)
# NVRTC comes from a pip wheel so that no CUDA toolkit / sudo is needed:
#   uv pip install --target ~/cuda-libs nvidia-cuda-nvrtc-cu12==12.9.86
export LD_LIBRARY_PATH="$HOME/cuda-libs/nvidia/cuda_nvrtc/lib:${LD_LIBRARY_PATH:-}"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$HOME/turmite-target}"
