# OJ_CodeExecutor

A server side application to process requests to run code submitted by the user thorugh th OJ frontend.

## Build/Run Instructions (Go)
cd into the ojserver directory and run 

```
go mod tidy
go build
```

Then run
```
./ojserver
```

## Build/Run Instructions (Python)

cd into OJExec-Python directory and run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask run
```