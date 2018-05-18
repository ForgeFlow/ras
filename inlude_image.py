from flask import Flask
from flask import send_file
from PIL import Image

app = Flask(__name__)

@app.route("/")
def hello():
    img = Image.new('RGB', (200, 100), (255, 255, 255))
    img.save('output.png')
    return send_file('output.png', mimetype='image/png')

if __name__ == "__main__":
    app.run()
