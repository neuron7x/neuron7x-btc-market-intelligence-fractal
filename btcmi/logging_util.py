import json, sys, time, uuid, random
def _ts(): return int(time.time()*1000)
def new_trace_id(seed: int | None = None, deterministic: bool = False):
    if deterministic and seed is not None:
        rng = random.Random(seed)
        return uuid.UUID(int=rng.getrandbits(128)).hex
    return uuid.uuid4().hex
def log(level, msg, **fields):
    rec={"level":level,"msg":msg,"ts":_ts(),**fields}
    sys.stderr.write(json.dumps(rec, ensure_ascii=False)+"\n"); sys.stderr.flush()
