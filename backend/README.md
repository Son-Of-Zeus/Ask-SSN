# Backend for ASkSSN Bot

## Installation instructions
- Install uv in your computer
- Change to the backend folder
```
cd backend
```
- Install all the dependencies with uv
```
uv sync
```
- Create a .env file inside backend, with the following content.
```
GEMINI_API_KEY='<Your-Api-Key>'
```
> Obtain the api key from https://aistudio.google.com/


## Running the server.

- Run the uvicorn server:
```
uv run  uvicorn main:app --reload
```

To access the docs:
```
http://127.0.0.1:8000/docs/
```