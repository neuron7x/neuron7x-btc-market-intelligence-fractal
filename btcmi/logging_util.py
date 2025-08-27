import json, sys, time, uuid
def _ts(): return int(time.time()*1000)
def new_trace_id(): return uuid.uuid4().hex
def log(level, msg, **fields):
    rec={"level":level,"msg":msg,"ts":_ts(),**fields}
    sys.stderr.write(json.dumps(rec, ensure_ascii=False)+"\n"); sys.stderr.flush()
