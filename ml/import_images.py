"""Import your licensed, verified ISL images: dataset/<session>/<label>/*.jpg.
Start FastAPI first. Session identities must describe independent recordings.
"""
import argparse
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen
import cv2

def post(route, payload):
    req=Request('http://127.0.0.1:8000/'+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urlopen(req,timeout=30) as r:
        return json.load(r)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset',type=Path)
    args=parser.parse_args()
    saved=skipped=0
    for path in args.dataset.glob('*/*/*'):
        if path.suffix.lower() not in {'.jpg','.jpeg','.png'}:
            continue
        img=cv2.imread(str(path))
        if img is None:
            skipped+=1;continue
        h,w=img.shape[:2];scale=min(640/w,480/h,1)
        img=cv2.resize(img,(int(w*scale),int(h*scale)))
        ok,jpg=cv2.imencode('.jpg',img)
        if not ok:
            skipped+=1;continue
        result=post('frame',{'image':base64.b64encode(jpg).decode()})
        if result['features'] is None:
            skipped+=1;continue
        post('sample',{'label':path.parent.name.upper(),'session':path.parent.parent.name,'features':result['features']})
        saved+=1
    print(json.dumps({'saved':saved,'skipped':skipped}))
