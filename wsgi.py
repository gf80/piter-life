import os
import sys
 
# TODO Надо поменять значение сайт на свой
activate_this = os.path.expanduser('~/сайт/venv/bin/activate_this.py')
exec(open(activate_this).read(), {'__file__': activate_this})
 
sys.path.insert(1, os.path.expanduser('~/сайт/public_html/'))
 
from django.core.wsgi import get_wsgi_application
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
 
application = get_wsgi_application()