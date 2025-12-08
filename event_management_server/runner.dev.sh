echo "Checking for migrations."
python manage.py migrate
echo "Migrations have already been made."

python manage.py collectstatic --noinput
echo "Collected static"
echo "Start server"
python manage.py runserver 0.0.0.0:8000