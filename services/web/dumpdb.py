import json
import sqlalchemy as sqAl
import os
from datetime import datetime
import hashlib
from pathlib import Path

dump_dir = os.environ["DUMP_FOLDER"]

Path(dump_dir).mkdir(exist_ok=True)

engine = sqAl.create_engine("postgresql+psycopg2://{user}:{passwd}@db:5432/{db}".format(
    user=os.environ["POSTGRES_USER"],
    passwd=os.environ["POSTGRES_PASSWORD"],
    db=os.environ["POSTGRES_DB"]))

meta = sqAl.MetaData()
meta.reflect(bind=engine) 

result = {}
for table in meta.sorted_tables:
    result[table.name] = [dict(row) for row in engine.execute(table.select())]

m = hashlib.new("ripemd160")
m.update(str(result).encode('utf-8'))

fp = "%s:%s" % (m.hexdigest(), datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))

print(fp)

#print(json.dumps(result, indent=4, default=str))