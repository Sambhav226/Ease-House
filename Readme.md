# Household Service App

1. Create a virtual env
# python3 -m venv mad-2

2. Activate the env
# source mad-2/bin/activate

3. Start the Back end
# cd back-end
# python3 app.py

4. Start the Front end
# cd front-end
Install nodes
# npm install
# npm run serve

5. Start Redis
# redis-server

6. Start Celery worker
# celery -A app.celery worker -l info

7. Start Celery beat
# celery -A main.celery beat --max-interval 1 -l info

8. Start mailhog
# mailhog
