"""Load reviewed Stage 3 definitions only; never execute the benchmark sweep."""
import ast
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re

SOURCE_BLOB = "42132bda2aea58c4e209170e4899997bfa5ada07"

def load_stage3():
    path=Path(__file__).resolve().parents[1]/"stage3.ipynb"
    data=path.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if blob != SOURCE_BLOB:
        raise ValueError("Historical notebook changed; review the loader before executing it")
    nb=json.loads(data)
    sources=[''.join(c.get('source',[])) for c in nb['cells']]
    outputs=''.join(''.join(o.get('text',[])) for o in nb['cells'][2].get('outputs',[]))
    fit=re.search(r'c0 = ([^ ]+) c1 = ([^ ]+) c2 = ([^\s]+)',outputs)
    if not fit: raise ValueError("saved fit coefficients missing")
    env={'__name__':'historical_stage3',**dict(zip(('c0','c1','c2'),map(float,fit.groups())))}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(sources[0],"stage3:cell0","exec"),env)
        exec(compile(sources[3],"stage3:cell3","exec"),env)
        exec(compile(sources[4].split('# Exact oracle over')[0],"stage3:cell4_setup","exec"),env)
        for i in (5,6,7):
            tree=ast.parse(sources[i])
            assert all(isinstance(x,(ast.FunctionDef,ast.Expr)) for x in tree.body)
            exec(compile(tree,f"stage3:cell{i}","exec"),env)
    env['audit_provenance']={'git_blob':blob,'sha256':hashlib.sha256(data).hexdigest(),
        'coefficient_source':'saved cell 2 output; simulator and fit NOT rerun',
        'coefficients':{k:env[k] for k in ('c0','c1','c2')},
        'executed_cells':'0,3,4 before oracle loop; function definitions from 5,6,7'}
    return env,nb
