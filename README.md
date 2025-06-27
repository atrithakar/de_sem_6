# Sem 6 DE Project - Farm Assistant 

## Requirements
- Python 3.12
- MongoDB

## How To Run

Step 1: Create a Virtual Environment
```
python -m venv de_env
```

Step 2: Activate the Virtual Environment
```
.\de_env\Scripts\activate
```

Step 3: Install the Requirements
```
pip install -r requirements.txt
```

Step 4: Start the Sender Service
```
cd ./sender
uvicorn main:app --reload --port 8000
```
> **Note: The sender service sends dummy data to the main server to simulate the data coming from real IOT devices.**

Step 5: Start Main Server
```
cd ./receiver
uvicorn main:app --reload --port 8001
```

Step 6: Type `http://localhost:8001` in browser to access the dashboard