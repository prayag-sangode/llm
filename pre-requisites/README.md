## 🔧 Prerequisites for Running vLLM Auto-Benchmarking on a GPU VM (A100)

Deploying and benchmarking open-source LLMs such as **Mistral**, **LLaMA**, and **Phi-3** using [vLLM](https://github.com/vllm-project/vllm) requires a properly prepared environment. This article outlines all the essential **system**, **GPU**, and **Python dependencies** to get started — especially on cloud VMs like **Open Telekom Cloud (OTC)** with A100 GPUs.

---

### Provision a Compatible GPU VM

Choose a GPU VM with at least the following:

| Resource | Minimum Recommendation |
| -------- | ---------------------- |
| **GPU**  | NVIDIA A100 80GB PCIe  |
| **CPU**  | 8 vCPUs                |
| **RAM**  | 64 GB                  |
| **Disk** | 500 GB SSD             |
| **OS**   | Ubuntu 22.04 LTS       |

---

### Install NVIDIA Driver & CUDA Runtime

OTC does **not install GPU drivers** by default. Follow these steps:

#### Add NVIDIA APT Repo:

```bash
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/nvidia-container.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container.list
sudo apt update
```

#### Install Driver + Container Toolkit:

```bash
sudo apt install -y nvidia-driver-550 nvidia-container-toolkit
```

#### Reboot and Verify:

```bash
sudo reboot
nvidia-smi
```

You should see your A100 GPU listed.

---

### Install Docker with GPU Runtime

#### a. Install Docker:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

#### b. Enable GPU support:

```bash
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

#### c. Test:

```bash
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

---

### Create Python Environment

```bash
# Create and activate virtualenv
python3 -m venv env
source env/bin/activate
```

---

### Install Python Dependencies

Create a `requirements.txt`:

```text
--extra-index-url https://download.pytorch.org/whl/cu121

torch==2.1.2+cu121
torchvision==0.16.2+cu121
torchaudio==2.1.2+cu121
vllm==0.4.0
transformers==4.42.1
accelerate==0.30.1
sentencepiece==0.2.0
mlflow==2.12.1
python-dateutil==2.9.0.post0
pyyaml==6.0.1
requests==2.32.2
tqdm==4.66.4
```

Install:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Validate GPU Access via PyTorch

```bash
python3 -c "import torch; print(torch.cuda.get_device_name(0))"
```

Expected:

```
NVIDIA A100 80GB PCIe
```

---

### `.gitignore` (Recommended)

```gitignore
__pycache__/
env/
*.log
mlruns/
*.json
*.csv
*.pt
.vscode/
```

---

##You're Ready!

Now you can run your benchmarking scripts using `vllm`, log results with `mlflow`, and automate model testing across different LLM variants.

Let me know if you'd like a follow-up article on:

* Automating benchmarking on new Docker image releases
* Using MLflow to visualize performance metrics
* Running benchmarks across multiple models with `models.yaml`

---

