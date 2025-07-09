- ทดสอบบน
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
- Prepare Docker GPU
  1. sudo rm /etc/apt/sources.list.d/nvidia-docker.list
  2. เพิ่ม keyring ใหม่
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  3. distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] \
https://nvidia.github.io/libnvidia-container/stable/$distribution/amd64 /" | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
  4. sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
  5. sudo systemctl restart docker

- How to run
  1. sudo docker build -t thai-tts-api .
  2. sudo docker run --gpus all -p 8000:8000 --rm --name thai-tts-api thai-tts-api
- ตรวจสอบว่าใช้ CUDA หรือไม่
  python -c "import torch; print(torch.cuda.is_available())"

- การทดสอบส่งเข้า API
curl -X POST http://localhost:8000/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"สวัสดีครับ ผมคือเสียงชายไทย", "voice":"thai-male"}' --output thai-male.wav

curl -X POST http://localhost:8000/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"สวัสดีค่ะ ดิฉันคือเสียงหญิงไทย", "voice":"thai-female"}' --output thai-female.wav

curl -X POST http://localhost:8000/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, I am the English male voice.", "voice":"english-male"}' --output english-male.wav

curl -X POST http://localhost:8000/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi, I am the English female voice.", "voice":"english-female"}' --output english-female.wav

- API
  http://localhost:8000/docs





