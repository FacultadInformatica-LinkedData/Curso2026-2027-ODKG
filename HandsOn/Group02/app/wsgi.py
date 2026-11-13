"""WSGI entry point (PythonAnywhere, gunicorn, ...).

PythonAnywhere: in the Web tab, open the WSGI configuration file and replace
its contents with (adjust the path to your clone):

    import sys
    path = "/home/<username>/Curso2026-2027-ODKG/HandsOn/Group02/app"
    if path not in sys.path:
        sys.path.insert(0, path)
    from wsgi import application

gunicorn:  gunicorn --chdir HandsOn/Group02/app wsgi:application
"""
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app import create_app  # noqa: E402

application = create_app()
