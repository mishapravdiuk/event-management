echo "Checking for migrations."
if ! python manage.py migrate --check
then
  echo "No migrations have been made."
  python manage.py migrate
else
  echo "Migrations have already been made."
fi

python manage.py collectstatic --noinput
echo "Collected static"
echo "Start server"
python manage.py runserver 0.0.0.0:8000