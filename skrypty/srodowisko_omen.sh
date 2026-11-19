#!/bin/sh
# Środowisko na OMENie (konto hackathon, ~/venv): torch z CUDA dla GTX 1050 (sm_61) + sonda karty.
set -e
nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader
pip install -q numpy scipy pillow
sonda() { python -c "import torch,torchvision;assert torch.cuda.is_available();x=torch.randn(512,512,device='cuda');torch.fft.rfft2(x);torch.nn.functional.conv2d(x[None,None],torch.randn(1,1,3,3,device='cuda'));torch.cuda.synchronize();print('SONDA OK',torch.__version__,torch.version.cuda,torch.cuda.get_device_name(0),torch.cuda.get_device_capability(0))"; }
if ! sonda 2>/dev/null; then
  echo "instaluję torch (cu126)…"
  pip install -q -r requirements.txt || true
  if ! sonda; then
    echo "cu126 bez sm_61 — instaluję torch 2.7.1 cu118"
    pip install -q --force-reinstall torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu118
    sonda
  fi
fi
