import os
import subprocess
from datetime import datetime
from fdata.db.configure import Configuration


def export_db(db_name, file_name=None):
    if file_name is None:
        file_name = datetime.now().strftime("%Y%m%d%H%M%S")
    c = Configuration()
    cmd = [c._mysqldump,
           f"--password={c._password}",
           f"--user={c._user}",
           f"--host={c._host}",
           f"--port={c._port}",
           f"{db_name}"]
    output_file = c._base_db_path+file_name+".sql"
    with open(output_file, "w") as f:
        subprocess.run(cmd, stdout=f)


def import_db(db_name, file_name=None):
    c = Configuration()
    if file_name is None:
        file_name = os.listdir(c._base_db_path)[-1].replace(".sql","")
    cmd = [c._mysql,
           f"--password={c._password}",
           f"--user={c._user}",
           f"--host={c._host}",
           f"--port={c._port}",
           f"{db_name}"]
    input_file = c._base_db_path+file_name+".sql"
    with open(input_file, "r") as f:
        subprocess.run(cmd, stdin=f)
