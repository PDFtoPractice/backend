# backend

<!-- 
## Virtual Environment Setup

This allows you to install all the Python dependencies in a "box" so they are not globally installed and don't clash with other projects.

1. Install [virtualenv](https://virtualenv.pypa.io/en/stable/): pip install virtualenv
2. Install [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html): pip install virtualenvwrapper *You can skip this and use virtualenv installed in a step before directly, virtualenvwrapper allows for nice interfacing with virtualenv
3. Source the `virtualenvwrapper: source /usr/local/bin/virtualenvwrapper.sh` NOTE: To help do this automatically on every new shell you open add the line above to your `.bash_profile` or `.bashrc`
4. Create a new env for the project: `mkvirtualenv pdftopractice`
 -->
## Virtual Environment Setup

1. Create a [venv](https://docs.python.org/3/library/venv.html) using `python3 -m venv pdftopractice`. 
2. Source the venv using `source pdftopractice/bin/activate` (path to activate)

## Clone the repo 

1. Get the code: `https://github.com/PDFtoPractice/backend.git`

## Install Python dependencies 

1. Go inside the `backend` directory: `cd backend`

## Deactivate the virtual environment 

1. Run `deactivate` 

## Database 

.. to be updated

## Running the project locally

1. Go inside the django app directory: cd pdfbackend
2. Run django server: python manage.py runserver
3. Go to 127.0.0.1:8000
4. You may see a message that you have unapplied migrations. When you see this simply run the command below which will create any tables and fields in the database: python manage.py migrate
