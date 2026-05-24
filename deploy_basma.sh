#!/bin/bash

# Define log file
LOG_FILE="server.log"

# Define Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CLEAR='\033[0m'

# Check for "logs" command
if [ "$1" == "logs" ]; then
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}=== Displaying logs (Press Ctrl+C to exit) ===${CLEAR}"
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}[!] Log file $LOG_FILE not found!${CLEAR}"
    fi
    exit 0
fi

# Check for "stop" command
if [ "$1" == "stop" ]; then
    echo -e "${RED}[*] Stopping Django server and Ngrok...${CLEAR}"
    if [ -f ".django.pid" ]; then
        DJANGO_PID=$(cat .django.pid)
        echo -e "${BLUE}[*] Killing existing Django PID $DJANGO_PID...${CLEAR}"
        kill -9 "$DJANGO_PID" 2>/dev/null || true
        rm -f .django.pid
    else
        pkill -f "manage.py runserver" || true
    fi

    if [ -f ".ngrok_wrapper.pid" ]; then
        WRAPPER_PID=$(cat .ngrok_wrapper.pid)
        echo -e "${BLUE}[*] Killing existing Ngrok wrapper PID $WRAPPER_PID...${CLEAR}"
        kill -9 "$WRAPPER_PID" 2>/dev/null || true
        rm -f .ngrok_wrapper.pid
    else
        pkill -f "start_ngrok.py" || true
    fi

    if [ -f ".ngrok.pid" ]; then
        NGROK_PID=$(cat .ngrok.pid)
        echo -e "${BLUE}[*] Killing existing Ngrok PID $NGROK_PID...${CLEAR}"
        kill -9 "$NGROK_PID" 2>/dev/null || true
        rm -f .ngrok.pid
    fi

    pkill -x ngrok || true
    echo -e "${GREEN}[✔] Stopped successfully.${CLEAR}"
    exit 0
fi

echo -e "${BLUE}==============================================${CLEAR}"
echo -e "${GREEN}      تنصيب وتشغيل مشروع بصمة قنا في الخلفية     ${CLEAR}"
echo -e "${BLUE}==============================================${CLEAR}"

# Terminate existing sessions to avoid port conflicts
echo -e "${BLUE}[*] Stopping existing instances...${CLEAR}"
if [ -f ".django.pid" ]; then
    DJANGO_PID=$(cat .django.pid)
    kill -9 "$DJANGO_PID" 2>/dev/null || true
    rm -f .django.pid
else
    pkill -f "manage.py runserver" || true
fi

if [ -f ".ngrok_wrapper.pid" ]; then
    WRAPPER_PID=$(cat .ngrok_wrapper.pid)
    kill -9 "$WRAPPER_PID" 2>/dev/null || true
    rm -f .ngrok_wrapper.pid
else
    pkill -f "start_ngrok.py" || true
fi

if [ -f ".ngrok.pid" ]; then
    NGROK_PID=$(cat .ngrok.pid)
    kill -9 "$NGROK_PID" 2>/dev/null || true
    rm -f .ngrok.pid
fi

pkill -x ngrok || true

# 1. Check for Virtual Environment
if [ -d "venv" ]; then
    echo -e "${GREEN}[✔] تم العثور على بيئة العمل الافتراضية (venv)${CLEAR}"
else
    echo -e "${YELLOW}[!] بيئة العمل الافتراضية غير موجودة. جاري إنشائها...${CLEAR}"
    python3 -m venv venv
    echo -e "${GREEN}[✔] تم إنشاء بيئة العمل الافتراضية بنجاح.${CLEAR}"
fi

# Activate venv
echo -e "${BLUE}[*] جاري تفعيل بيئة العمل الافتراضية...${CLEAR}"
source venv/bin/activate

# 2. Install / Upgrade pip and requirements
echo -e "${BLUE}[*] جاري تحديث pip وتثبيت المكتبات المطلوبة...${CLEAR}"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[✔] تم تثبيت جميع المكتبات بنجاح.${CLEAR}"
else
    echo -e "${RED}[!] ملف requirements.txt غير موجود!${CLEAR}"
    exit 1
fi

# 3. Database Migrations and Seeding
echo -e "${BLUE}[*] جاري تحضير وتطبيق قواعد البيانات (Migrations)...${CLEAR}"
python3 manage.py makemigrations portal
python3 manage.py migrate
echo -e "${BLUE}[*] جاري استيراد البيانات الافتراضية (Seeding)...${CLEAR}"
python3 manage.py seed_data
echo -e "${GREEN}[✔] تم تطبيق قاعدة البيانات واستيراد البيانات بنجاح.${CLEAR}"

# 4. Collect Static Files
echo -e "${BLUE}[*] جاري تجميع الملفات الثابتة (Static Files)...${CLEAR}"
python3 manage.py collectstatic --noinput
echo -e "${GREEN}[✔] تم تجميع الملفات الثابتة بنجاح.${CLEAR}"

# 5. Launch in background
echo -e "${BLUE}[*] Starting Django & Ngrok in background...${CLEAR}"
# Truncate log file
> "$LOG_FILE"

nohup python3 manage.py runserver 127.0.0.1:8005 >> "$LOG_FILE" 2>&1 &
echo $! > .django.pid

nohup python3 start_ngrok.py >> "$LOG_FILE" 2>&1 &
echo $! > .ngrok_wrapper.pid

echo -e "${GREEN}[✔] Django and Ngrok started in background!${CLEAR}"
echo -e "${YELLOW}Logs are being written to $LOG_FILE${CLEAR}"
echo -e "${BLUE}Run: ./deploy_basma.sh logs to view output.${CLEAR}"
echo -e "${BLUE}Run: ./deploy_basma.sh stop to stop services.${CLEAR}"
echo -e "\nShowing initial logs (waiting for Ngrok URL...):"
sleep 4
cat "$LOG_FILE"
