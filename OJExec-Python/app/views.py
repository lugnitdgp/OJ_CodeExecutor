import os
from app import app
from flask import request
from config import enginedir, staticdir, engine_path
from app.models import File
from urllib.request import urlretrieve
from app import db


def status():
    make_temp_status = "sudo cat usage.txt > temp_file"
    os.system(make_temp_status)
    with open("temp_file", "r") as f:
        stat = f.read().split("\n")
        return {
            'run_status': stat[0],
            'elapsed_time': int(stat[1].split(":")[1].strip().split(" ")[0]),
            'memory_taken': int(stat[2].split(":")[1].strip().split(" ")[0]),
            'cpu_time': float(stat[3].split(":")[1].strip().split(" ")[0])
        }


def compare(path1, path2):
    compare_code = os.system("diff -q "+path1+" "+path2)
    if compare_code == 0:
        return True
    else:
        return False


def run(f, time, mem, input_file, temp_output_file, output_file, compile_command, run_command):
    os.system(compile_command.format(f))

    if (os.stat("compile_log").st_size != 0):
        with open("compile_log", "r+") as temp_file:
            return {
                "code": 1,
                "message": temp_file.read()
            }

    else:
        params = {
            "engine_path": engine_path, "time": time, "mem": mem, "f": f,
            "outpath": os.path.abspath(enginedir),
            "in_file": input_file, "temp_out_file": temp_output_file
        }
        runner = run_command.format(**params)
        os.system(runner)
        stat = status()
        res = None

        if (stat['run_status'] == "OK"):
            if (compare(output_file, temp_output_file)):
                stat['run_status'] = "AC"
                res = {  # Passed
                    "code": 0,
                    "status": stat
                }
            else:
                stat['run_status'] = "WA"
                res = {  # Failed
                    "code": 0,
                    "status": stat
                }
        else:
            res = {"code": 2, "status": stat}
        return res


@app.route("/", methods=["POST"])
def home():
    exec_args = request.json.get("args")
    try:
        with open(os.path.join(enginedir, exec_args["filename"]), "w+") as file:
            file.write(exec_args["code"])
            file.close()
    except:
        print("File I/O Error")
    code_file = os.path.join(enginedir, exec_args["filename"])

    input_file_urls = request.json.get("input_file_urls")
    output_file_urls = request.json.get("output_file_urls")

    input_file_hash = request.json.get("input_file_hashes")
    output_file_hash = request.json.get("output_file_hashes")

    input_testfile = ""
    output_testfile = ""
    temp_output_file = os.path.join(staticdir, exec_args["filename"].split(".")[0]+".txt")

    net_res = []

    for (index, url) in enumerate(input_file_urls, start=0):
        if bool(File.query.filter_by(file_hash=input_file_hash[index]).first()):
            input_testfile = File.query.filter_by(
                file_hash=input_file_hash[index]).first().path
        else:
            input_testfile = urlretrieve(url, os.path.join(
                staticdir, input_file_urls[index].split("/")[-1]))[0]
            file = File(file_hash=input_file_hash[index], path=input_testfile)
            db.session.add(file)
            db.session.commit()

        if bool(File.query.filter_by(file_hash=output_file_hash[index]).first()):
            output_testfile = File.query.filter_by(
                file_hash=output_file_hash[index]).first().path

        else:
            output_testfile = urlretrieve(url, os.path.join(
                staticdir, output_file_urls[index].split("/")[-1]))[0]
            file = File(
                file_hash=output_file_hash[index], path=output_testfile)
            db.session.add(file)
            db.session.commit()
        res = run(code_file, exec_args["time"], exec_args["mem"], input_testfile, temp_output_file,
            output_testfile, exec_args["compile_command"], exec_args["run_command"])
        net_res.append(res)
    return net_res
