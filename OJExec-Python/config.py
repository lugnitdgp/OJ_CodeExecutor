from decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))

enginedir = os.path.abspath(os.path.join(basedir, "safeexec"))

engine_path = os.path.join(enginedir, "safeexec")

staticdir = os.path.abspath(os.path.join(basedir, "static"))