# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# NOTE
# =======
#
# This is a really disgusting script that **should not be used in absolutely any circumstances**.
#
# No, I am not joking, if you use this script for anything, you are an # idiot. Don't be an idiot,
# don't use it.
#

import json
import sqlalchemy as sqAl
import os
from datetime import datetime
import hashlib
from pathlib import Path
import glob


def write_json(result, fp):
    with open(os.path.join(os.environ["DUMP_FOLDER"], fp), "w") as o:
        json.dump(result, o, indent=4, default=str)


Path(os.environ["DUMP_FOLDER"]).mkdir(exist_ok=True)

engine = sqAl.create_engine(
    "postgresql+psycopg2://{user}:{passwd}@db:5432/{db}".format(
        user=os.environ["POSTGRES_USER"],
        passwd=os.environ["POSTGRES_PASSWORD"],
        db=os.environ["POSTGRES_DB"],
    )
)

meta = sqAl.MetaData()
meta.reflect(bind=engine)

result = {}
for table in meta.sorted_tables:
    result[table.name] = [dict(row) for row in engine.execute(table.select())]

m = hashlib.new("ripemd160")
m.update(str(result).encode("utf-8"))
h = m.hexdigest()

fp = "%s:%s.json" % (h, datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))

if os.listdir(os.environ["DUMP_FOLDER"]) != []:
    glob_dir = os.path.join(os.environ["DUMP_FOLDER"], "*")
    newest = max(glob.glob(glob_dir), key=os.path.getctime)
    if newest.split(":")[0].split("/")[-1] != h:
        write_json(result, fp)
else:
    write_json(result, fp)
