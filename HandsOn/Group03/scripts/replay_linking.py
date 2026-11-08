"""Replay the saved linking histories in a local OpenRefine instance (stdlib only)."""
import argparse
import csv
import io
import json
from pathlib import Path
import time
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
import uuid

ROOT = Path(__file__).resolve().parents[1]


def replay(base_url, names):
    base_url = base_url.rstrip('/')
    def get(command, **params):
        for attempt in range(5):
            payload=urlopen(base_url+'/command/core/'+command+'?'+urlencode(params),timeout=30).read()
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                if attempt==4:
                    raise RuntimeError(f'OpenRefine returned invalid JSON for {command}')
                time.sleep(0.5)
    token=get('get-csrf-token')['token']
    def post(command, params, **query):
        query['csrf_token']=token
        request=Request(base_url+'/command/core/'+command+'?'+urlencode(query),
                        data=urlencode(params).encode(),method='POST')
        return urlopen(request,timeout=60)
    for name in names:
        source=ROOT/'csv'/f'{name}-updated.csv'
        ops=json.loads((ROOT/'lodrefine'/f'{name}-with-links.json').read_text())
        boundary='Group03'+uuid.uuid4().hex
        options={'encoding':'UTF-8','separator':',','ignoreLines':-1,'headerLines':1,
                 'skipDataLines':0,'limit':-1,'storeBlankRows':False,
                 'guessCellValueTypes':False,'processQuotes':True,'storeBlankCellsAsNulls':True}
        parts=[]
        for key,value in [('project-name','Group03 validation '+name+' '+uuid.uuid4().hex[:8]),
                          ('format','text/line-based/*sv'),('options',json.dumps(options))]:
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="project-file"; filename="{source.name}"\r\nContent-Type: text/csv\r\n\r\n'.encode()+source.read_bytes()+b'\r\n')
        parts.append(f'--{boundary}--\r\n'.encode())
        request=Request(base_url+'/command/core/create-project-from-upload?'+urlencode({'csrf_token':token}),
                        data=b''.join(parts),headers={'Content-Type':'multipart/form-data; boundary='+boundary})
        response=urlopen(request,timeout=60)
        project=parse_qs(urlsplit(response.geturl()).query)['project'][0]
        print(name,'created temporary OpenRefine project',project,flush=True)
        try:
            result=json.load(post('apply-operations',{'operations':json.dumps(ops,ensure_ascii=False)},project=project))
            if result.get('code') not in ('ok','pending'):
                raise RuntimeError(result)
            deadline=time.monotonic()+900
            while True:
                processes=get('get-processes',project=project).get('processes',[])
                if not processes: break
                if any(p.get('status')=='error' for p in processes): raise RuntimeError(processes)
                if time.monotonic()>deadline: raise TimeoutError(processes)
                time.sleep(1)
            columns=get('get-models',project=project)['columnModel']['columns']
            export_options={'format':'csv','separator':',','lineSeparator':'\n','encoding':'UTF-8',
                            'outputColumnHeaders':True,'outputBlankRows':False,'quoteAll':False,
                            'columns':[{'name':c['name'],'reconSettings':{'output':'cell-content',
                                        'blankUnmatchedCells':False,'linkToEntityPages':False}} for c in columns]}
            output=post('export-rows',{'engine':json.dumps({'facets':[],'mode':'row-based'}),
                                    'options':json.dumps(export_options)},project=project,format='csv').read()
            text=output.decode('utf-8-sig')
            rows=list(csv.DictReader(io.StringIO(text)))
            with source.open(encoding='utf-8-sig',newline='') as f: original=list(csv.DictReader(f))
            assert len(rows)==len(original),(name,len(rows),len(original))
            for actual,expected in zip(rows,original):
                assert all(actual[k]==v for k,v in expected.items()),(name,expected,actual)
                assert actual.get('district_wikidata',actual.get('station_district_wikidata','')).startswith('http://www.wikidata.org/entity/Q')
                if name=='terrazas_hosteleria': assert actual['neighbourhood_wikidata'].startswith('http://www.wikidata.org/entity/Q')
            target=ROOT/'csv'/f'{name}-with-links.csv'
            with target.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
                writer.writeheader();writer.writerows(rows)
            print(name,'PASS:',len(rows),'rows; all original cells preserved',flush=True)
        finally:
            result=json.load(post('delete-project',{},project=project))
            if result.get('code')!='ok': raise RuntimeError(result)
            print(name,'removed temporary validation project',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:3333')
    parser.add_argument('--dataset',choices=['estaciones_acusticas','terrazas_hosteleria','contaminacion_acustica'])
    args=parser.parse_args()
    replay(args.url,[args.dataset] if args.dataset else ['estaciones_acusticas','terrazas_hosteleria','contaminacion_acustica'])
