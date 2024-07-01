from data_collecting import image_processing_db
from data_collecting import data_fetch_db
import os
import sys
import django
from django.core.management import call_command
sys.path.append('web_app/')  # Adjust the path to your project root
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_app.settings')
django.setup()
def main():
    data_fetch_db.main()
    image_processing_db.main()
    call_command('makemigrations')
    call_command('migrate --fake')
    call_command('runserver', '127.0.0.1:8000')

if __name__ == '__main__':
    main()