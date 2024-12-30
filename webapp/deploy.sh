#!/bin/bash

# Run the get_version.py script
python pomo/get_version.py

# Collect static files
python manage.py collectstatic --noinput

# Restart Apache2
sudo systemctl restart apache2