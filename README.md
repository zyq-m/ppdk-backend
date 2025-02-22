# PPDK Flask

PPDK Info Sys using Flask

## Installation

1. Clone the repository:

```bash
git clone https://github.com/zyq-m/ppdk-backend.git
cd ppdk-backend
```

2. Create and activate a virtual environment: (mac os)

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install

```bash
pip install -r requirements.txt
```

## Running application

1. Run the app:

```bash
python3 app.py
```

2. Deploy

Execute this command one-by-one

```bash
cd var/www/ppdk-backend
git pull
source .venv/bin/activate
pip install -r requirement.txt
deactivate
sudo systemctl restart ppdk-backend
sudo systemctl restart nginx
```
