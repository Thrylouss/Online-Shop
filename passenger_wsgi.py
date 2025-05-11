import os
import sys

########################################
# 1) Пути к вашему проекту и виртуалке #
########################################
PROJECT_PATH = "/home/host6049/online-shop.milliybiz.uz"
VENV_ACTIVATE = "/home/host6049/virtualenv/online-shop.milliybiz.uz/3.10/bin/activate_this.py"

########################################
# 2) Добавляем PROJECT_PATH в sys.path #
########################################
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

##############################################
# 3) Активируем виртуальное окружение, если есть
##############################################
try:
    with open(VENV_ACTIVATE) as f:
        code = compile(f.read(), VENV_ACTIVATE, "exec")
        exec(code, dict(__file__=VENV_ACTIVATE))
except FileNotFoundError:
    # Если виртуальное окружение не используется или путь неверен,
    # этот блок можно убрать.
    pass

########################################################
# 4) Указываем DJANGO_SETTINGS_MODULE и импортируем WSGI
########################################################
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OnlineShopProject.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

########################################################
# 5) Подключаем WhiteNoise и раздаём также /media/
########################################################
from whitenoise import WhiteNoise

# Оборачиваем наше приложение в WhiteNoise
application = WhiteNoise(application)

# Предположим, ваш MEDIA_ROOT = BASE_DIR / "media", а в settings.py:
# MEDIA_URL = '/media/'
# Тогда, если PROJECT_PATH указывает на корень проекта, 
# папка media лежит в "/home/host6049/online-shop.milliybiz.uz/Online-Shop/media"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

# Добавляем папку media c префиксом /media/
application.add_files(MEDIA_ROOT, prefix="/media/")
