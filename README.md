# API keys application

This is my one of the first tries to make API authorization.
Basically, this application allows you to create your own secure API key. Sign in by the key, and get short-lived JWT _(JSON Web Token)_.

# Usage

**Clone the repository:**
```bash
git clone https://github.com/yeghor/RestAPI-With-API-keys-Auth.git
```
**Move to the application directory, create virtual enviroment _(optional)_, activate it and install dependencies:**
```bash
cd RestAPI-With-API-keys-Auth

python -m venv myvenv
myenv/Scripts/activate.bat # Activate venv

pip install -r requirements.txt
```
**Move to the main directory and start the application:**
```bash
cd API_application
uvicorn main:app --reload
```

Acces the **API** by this URL:
[http://localhost:8000](http://localhost:8000)
