#AI #gemma #instructions

## 0. Install Podman

> **PowerShell (Admin)**

- [ ] `winget install RedHat.Podman`

## 1. Install NVIDIA Container Toolkit

> **WSL Ubuntu**

- [ ] `curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg`
- [ ] `curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list`
- [ ] `sudo apt update && sudo apt install -y nvidia-container-toolkit`

## 2. Start Ollama Container with GPU

> **PowerShell**

- [ ] `podman run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`

## 3. Pull Gemma 4

> **PowerShell**

- [ ] `podman exec -it ollama ollama pull gemma4:e2b`

## 4. Start Open WebUI

> **PowerShell**

- [ ] `podman run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main`

## 5. Connect Open WebUI to Ollama

> **Browser at `localhost:3000`**

- [ ] Go to **Admin Panel** → **Settings** → **Connections**
- [ ] Set Ollama URL to `http://host.docker.internal:11434`

## 6. Enable Web Search (optional)

> **Browser at `localhost:3000`**

- [ ] Go to **Admin Panel** → **Settings** → **Web Search**
- [ ] Enable with DuckDuckGo (no API key needed)

## 7. HTTPS for Remote Access via Tailscale (optional)

> **PowerShell (Admin)**

- [ ] `tailscale serve 3000`

---

Access the chat at `localhost:3000` locally or via your Tailscale HTTPS URL from other devices.