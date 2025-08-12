#!.venv/bin/python3
import subprocess
import traceback
import json
import os
import io
import base64

from zipfile import ZipFile, ZIP_DEFLATED

####################################################################
# Zip Code and dependencies
####################################################################
def createZippedFunctionCode(packDependencies: bool):
    # create temp venv, installdependencies
    if packDependencies:
        subprocess.run(["./packDependencies.sh", ""], shell=True)

    # zip_buffer = io.BytesIO()

    with ZipFile("./code.zip", "w", ZIP_DEFLATED) as zip:
        # add files from folder src
        src = "./src"

        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[absname.rindex("/src/") + len("/src/") :]
                #print("zipping %s as %s" % (os.path.join(dirname, filename), arcname))
                if (
                  "__pycache__" not in absname
                  and "__pycache__" not in arcname
                ):
                  #print("zipping %s as %s" % (os.path.join(dirname, filename), arcname))
                  zip.write(absname, arcname)

        # add files from dependencies
        src = "./target/dependenciesVenv/lib/python3.9/site-packages"

        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[
                    absname.rindex("/site-packages/") + len("/site-packages/") :
                ]
                if (
                    not arcname.startswith("pip")
                    and not arcname.startswith("_distutils")
                    and not arcname.startswith("setuptools")
                    and not arcname.startswith("uvloop")  # Not needed for Lambda/FunctionGraph
                    and not arcname.startswith("watchfiles")  # Not needed for production
                    and not arcname.startswith("httptools")  # Not needed, uvicorn dependency
                    and not arcname.startswith("websockets")  # Not needed for HTTP APIs
                    and not arcname.startswith("greenlet")  # SQLAlchemy async, not needed
                    and "__pycache__" not in absname
                    and "__pycache__" not in arcname
                    and ".egg-info" not in arcname
                ):
                    #print("zipping %s as %s" % (os.path.join(dirname, filename), arcname))
                    zip.write(absname, arcname)

    # encoded = base64.b64encode(zip_buffer.getvalue())

    # code = str(encoded, "utf-8")

    # print(f"############ Length of code: {len(code)}")
  
    

if __name__ == "__main__":
  createZippedFunctionCode(True)
