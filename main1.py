from fastapi import FastAPI

app = FastAPI(title="mini blog")

@app.get("/")

def home():
    return {'mensaje':'Bienvenidos a mi blog elian martinez'}