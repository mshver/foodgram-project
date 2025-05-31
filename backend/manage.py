import os
import sys

def bootstrap():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and available."
        ) from e
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    bootstrap()