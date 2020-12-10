import os
from urllib.request import urlretrieve
from urllib.parse import unquote
from flask import request, jsonify
from app import app, db
from config import enginedir, staticdir, engine_path
from app.models import File

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
    compare_code = os.system("diff -q " + path1 + " " + path2)
    if compare_code == 0:
        return True
    else:
        return False


def run(f, time, mem, input_file, temp_output_file, output_file, compile_command, run_command):
    os.system(compile_command.format(f))

    if (os.stat("compile_log").st_size != 0):
        with open("compile_log", "r+") as temp_file:
            return {"code": 1, "message": temp_file.read()}

    else:
        params = {
            "engine_path": engine_path,
            "time": time,
            "mem": mem,
            "f": f,
            "outpath": os.path.abspath(enginedir),
            "in_file": input_file,
            "temp_out_file": temp_output_file
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
    exec_args = request.json.get("exec_args")
    try:
        with open(os.path.join(enginedir, exec_args["filename"]), "w+") as file:
            file.write(unquote(exec_args["code"]))
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
    temp_output_file = os.path.join(staticdir, exec_args["filename"].split(".")[0] + ".txt")

    net_res = []

    for (index, url) in enumerate(input_file_urls, start=0):
        if bool(File.query.filter_by(file_hash=input_file_hash[index]).first()):
            input_testfile = File.query.filter_by(file_hash=input_file_hash[index]).first().path
        else:
            input_testfile = urlretrieve(url, os.path.join(staticdir, input_file_urls[index].split("/")[-1]))[0]
            file = File(file_hash=input_file_hash[index], path=input_testfile)
            db.session.add(file)
            db.session.commit()

        if bool(File.query.filter_by(file_hash=output_file_hash[index]).first()):
            output_testfile = File.query.filter_by(file_hash=output_file_hash[index]).first().path
        else:
            output_testfile = urlretrieve(url, os.path.join(staticdir, output_file_urls[index].split("/")[-1]))[0]
            file = File(file_hash=output_file_hash[index], path=output_testfile)
            db.session.add(file)
            db.session.commit()
        res = run(code_file, exec_args["time"], exec_args["mem"], input_testfile, temp_output_file, output_testfile,
                  exec_args["compile_command"], exec_args["run_command"])
        net_res.append(res)
    return jsonify(net_res)


'''
Sample JSON Request :
    {
        "input_file_urls": ["http://127.0.0.1:8000/media/testcases/ques_1/test_10/input1.in"],
        "output_file_urls": ["http://127.0.0.1:8000/media/testcases/ques_1/test_10/output1.out"],
        "input_file_hashes": ["395748230b7e2b63d1d729737fc050dae721fcc6959e2b59012aba404dfaa88fd6ed38b752154ee264058dc89412a2804440244e5fc0c97c7dd167349bdb1e3d"],
        "output_file_hashes": ["2b59d179d9815994f687383a886ea34109889756efca5ab27318cc67ce2a21261d12fa6fee6b8c716f72214ead55ee0d789d6c35cff977d40ef5728ba9188a80"],
        "exec_args" : {
            "code" : /// URI Encoded programming code received from the frontend without any manipulation in between
            "filename" : "testing.py",
            "time" : 1,
            "mem" : "..",
            "compile_command" : "...",
            "run_command" : "..."
        }
    }
'''