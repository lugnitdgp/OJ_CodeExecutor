#!/usr/bin/python3
import os
import sys
import json
import sqlite3
from urllib.request import urlretrieve
from urllib.parse import unquote
import django
from celery import Celery
from decouple import config
from settings import FILE_HASHES, enginedir, staticdir, engine_path

sys.dont_write_bytecode = True
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from accounts.models import *
from interface.models import *

app = Celery("tasks", broker=config("CELERY_BROKER_URL"))


def write_json(data, filename='file-info.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def putData(fhash, path):
    with open("file-info.json", "r") as fileInfo:
        data = json.load(fileInfo)
        data[fhash] = path
        write_json(data)


def checkData(fhash):
    with open("file-info.json", "r") as fileInfo:
        data = json.load(fileInfo)
    return fhash in data


def getData(fhash):
    with open("file-info.json", "r") as fileInfo:
        data = json.load(fileInfo)
    return data.get(fhash)


def db_store(user, result, ac, wa, job_id, contest, code, lang):
    j = Job(coder=user,
            code=code,
            status=json.dumps(result),
            AC_no=ac,
            WA_no=wa,
            job_id=job_id,
            contest=contest,
            timestamp=t.now(),
            lang=lang)
    j.save()


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


@app.task
def execute(coder, code, lang, contest, exec_args, input_file_urls, output_file_urls, input_file_hash,
            output_file_hash):
    user = Coder.objects.get(email=coder['email'])
    contest = Contest.objects.get(contest_code=contest['contest_code'])
    ac, wa = 0, 0
    language = contest.contest_langs.get(name=lang)
    ext = language.ext
    filename = execute.request.id.__str__() + "." + ext

    try:
        with open(os.path.join(enginedir, filename), "w+") as file:
            file.write(unquote(code))
            file.close()
    except IOError:
        print("File I/O Error")

    f = os.path.join(enginedir, filename)

    input_testfile = ""
    output_testfile = ""
    temp_output_file = os.path.join(staticdir, execute.request.id.__str__() + ".txt")

    net_res = []

    for (index, url) in enumerate(input_file_urls, start=0):
        if checkData(input_file_hash[index]):
            input_testfile = getData(input_file_hash[index])
        else:
            input_testfile = urlretrieve(url, os.path.join(staticdir, url.split("/")[-1]))[0]
            putData(input_file_hash[index], input_testfile)

        if checkData(output_file_hash[index]):
            output_testfile = getData(output_file_hash[index])
        else:
            temp_url = output_file_urls[index]
            output_testfile = urlretrieve(temp_url, os.path.join(staticdir, "_".join(temp_url.split("/")[-2:])))[0]
            putData(output_file_hash[index], output_testfile)
        res = run(f, exec_args["time"], exec_args["mem"], input_testfile, temp_output_file, output_testfile,
                  language.compile_command, language.run_command)
        net_res.append(res)

    for result in net_res:
        if (result['code'] == 1):
            break
        elif (result['code'] == 0 and result['status']['run_status'] == "AC"):
            ac += 1
        elif (result['code'] == 0 and result['status']['run_status'] == "WA"):
            wa += 1
    db_store(user, net_res, ac, wa, execute.request.id.__str__(), contest, code, lang)