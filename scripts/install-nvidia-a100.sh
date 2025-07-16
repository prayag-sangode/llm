#!/bin/bash
set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing base dependencies..."
sudo apt install -y curl wget gnupg lsb-release ca-certificates software-properties-common

echo "Adding NVIDIA GPG key and repo..."
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/nvidia-container.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container.list

echo "Updating package list..."
sudo apt update

echo "Installing NVIDIA driver and container toolkit..."
sudo apt install -y nvidia-driver-550 nvidia-container-toolkit

echo "Rebooting to activate driver..."
echo "After reboot, run: nvidia-smi"
echo "Then run: docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi"
sleep 3
sudo reboot

