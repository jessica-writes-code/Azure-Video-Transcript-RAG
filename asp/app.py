from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# Create a "templates" directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Mount static files directory (if you want to add CSS or JS files later)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/echo", response_class=HTMLResponse)
async def echo(request: Request, user_input: str = Form(...)):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "echo_message": f'"{user_input}" is what you entered.'},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
