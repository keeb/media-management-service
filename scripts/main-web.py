import os
import json
import random

from flask import Flask, render_template
from flask_cors import CORS
from lib.suicidegirls import Azhdar
from lib.file import get_folder_contents


IMAGE_DIRECTORY = os.path.join(os.getcwd(), "static/img")

images = []

def construct_href(full_path):
    # turns /storage/02/code/projects/media-assistant/static/img/
    # Sophoulla Photo Album_ old money _ SuicideGirls/002a1f382ae54145250330f9052e8017.jpg
    # into /static/img/Sophoulla Photo Album_ old money _ SuicideGirls/002a1f382ae54145250330f9052e8017.jpg
    path_list = full_path.split("/")
    count = 0
    for item in path_list:
        if item == "static":
            break
        count += 1
    
    rel_path = "/".join(path_list[count:])
    return "/%s" % rel_path


image_total = -1

try:
    a = Azhdar(IMAGE_DIRECTORY)
    for model in a.models():
        for album in model.albums():
            for image in album.photos():
                if len(images) == image_total: break
                image_path = construct_href(image.path)
                images.append(image_path)
except:
    for image in get_folder_contents(IMAGE_DIRECTORY):
        images.append("/static/img/%s" % image)


if len(images) == 0: exit(1)
random.shuffle(images)


app = Flask(__name__)

@app.route("/")
def main():
    image = images[random.randrange(len(images))]
    return render_template("index.html", image=image, images=json.dumps(images))


if __name__ == '__main__':
    CORS(app)
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=5000))