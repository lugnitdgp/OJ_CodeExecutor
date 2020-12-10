import os
from app import app
from flask import request
from config import enginedir, staticdir, engine_path
from app.models import File
from urllib.request import urlretrieve
from app import db


@app.route("/", methods=["POST"])
def home():
    # exec_args = request.json.get("args")
    # try:
    #     with open(os.path.join(enginedir, exec_args["filename"]), "w+") as file:
    #         file.write(exec_args["code"])
    #         file.close()
    # except:
    #     print("File I/O Error")
    # code_file = os.path.join(enginedir, exec_args["filename"])

    input_file_urls = request.json.get("input_file_urls")
    output_file_urls = request.json.get("output_file_urls")

    input_file_hash = request.json.get("input_file_hashes")
    output_file_hash = request.json.get("output_file_hashes")

    input_testfile = ""
    output_testfile = ""

    for (index,url) in enumerate(input_file_urls, start=0): 
        if bool(File.query.filter_by(file_hash=input_file_hash[index]).first()):
            input_testfile = File.query.filter_by(file_hash=input_file_hash[index]).first().path
        else:
            input_testfile = urlretrieve(url, os.path.join(staticdir,input_file_urls[index].split("/")[-1]))[0]
            file = File(file_hash=input_file_hash[index], path=input_testfile)
            db.session.add(file)
            db.session.commit()

        if bool(File.query.filter_by(file_hash=output_file_hash[index]).first()):
            output_testfile = File.query.filter_by(file_hash=output_file_hash[index]).first().path
            
        else:
            output_testfile = urlretrieve(url, os.path.join(staticdir,output_file_urls[index].split("/")[-1]))[0]
            file = File(file_hash=output_file_hash[index], path=output_testfile)
            db.session.add(file)
            db.session.commit()
    return {"message" : "done"}