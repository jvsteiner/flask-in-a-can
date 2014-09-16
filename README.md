# Flask in a Can

1. Clone repo:

    $ git clone git://github.com/jvsteiner/flask-in-a-can.git

2. Change directory:

    $ cd flask-in-a-can

3. Install dependencies:

    $ pip install -r requirements.text

4. Copy the example email config and edit the values, use env.py in production to override development settings:

    $ cp env/email.py.example config/email.py
    $ cp env/env.py.example config/env.py

5. Initialize, migrate and upgrade the database:

    $ python app.py db init
    $ python app.py db migrate
    $ python app.py db upgrade

5. Start the app:

    $ python app.py runserver

NOTE: layout.html uses a _scripts.html helper that references several javascript libraries that I like to use:

twitter bootstrap 3.2.0
jquery 1.8.2
knockout.js 2.2.1
knockout mapping plugin

The helper is set to use a CDN link when config.PRODUCTION == True, and serve from /static otherwise.  You will need to obtain local copies to work in development mode.

This project includes templates for registration, signin, password reset, password change, and user profile
I based it off mattupstate, who owns flask-security-example, and added some other functionality that I commonly use.  Hope you find it helpful.