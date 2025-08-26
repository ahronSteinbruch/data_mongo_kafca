import uvicorn
from fastapi import FastAPI
from dal.publisher import Publisher

app = FastAPI()
publisher = Publisher()
@app.get('/')
def index():
    return \
        {
        'status': 'OK',
            'my name': 'model trainer',
            'port': 8002
        }
@app.get('/data')
def fetch_data():
    publisher.publish()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)