#!/usr/bin/env python3
"""Read-only ECMA-335 IL call-site and dynamic-loader inventory.
Scans managed DLLs in a directory; does not modify input files.
Requires: dnfile, dncil
"""
import argparse, csv, json, os, re, sys, traceback
from collections import Counter
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes

CALL_OPS = {'call','callvirt','newobj','calli','ldftn','ldvirtftn'}
DYNAMIC_NAMES = {
 'loadlibrary','loadlibrarya','loadlibraryw','loadlibraryex','loadlibraryexa','loadlibraryexw',
 'getprocaddress','freelibrary','ldrloaddll','ldrgetprocedureaddress',
 'dlopen','dlsym','dlclose','android_dlopen_ext','mono_dl_open'
}
TOKEN_RE = re.compile(r'0x([0-9a-fA-F]{1,8})')

def s(v):
    if v is None: return ''
    try:
        return str(v)
    except Exception:
        return repr(v)

def rid_of(v):
    try: return int(v.row_index)
    except Exception: pass
    try: return int(v)
    except Exception: return 0

def token_value(opnd):
    if opnd is None: return None
    for attr in ('value','token','raw'):
        try:
            x=getattr(opnd,attr)
            if isinstance(x,int): return x
        except Exception: pass
    m=TOKEN_RE.search(s(opnd))
    return int(m.group(1),16) if m else None

def table_name(tok):
    return (tok >> 24) & 0xff

def token_rid(tok): return tok & 0x00ffffff

def get_name(row, attr='Name'):
    try: return s(getattr(row,attr))
    except Exception: return ''

def member_parent(row):
    try:
        c=row.Class
        rr=getattr(c,'row',None)
        if rr is None: return ''
        # TypeDef / TypeRef / ModuleRef coded-index parent
        nm=get_name(rr)
        ns=get_name(rr,'TypeNamespace')
        return (ns+'.' if ns else '')+nm
    except Exception: return ''

def build_owner_map(pe):
    owners={}
    try:
        tdefs=pe.net.mdtables.TypeDef.rows
        methods=pe.net.mdtables.MethodDef.rows
        starts=[]
        for tr in tdefs:
            ml=getattr(tr,'MethodList',None)
            if isinstance(ml,(list,tuple)):
                rid=rid_of(ml[0]) if ml else 0
            else:
                rid=rid_of(ml)
            if rid: starts.append((rid, tr))
        starts.sort(key=lambda x:x[0])
        for i,(start,tr) in enumerate(starts):
            end=(starts[i+1][0]-1) if i+1<len(starts) else len(methods)
            ns=get_name(tr,'TypeNamespace'); name=get_name(tr)
            full=(ns+'.' if ns else '')+name
            for rid in range(start,end+1): owners[rid]=full
    except Exception: pass
    return owners

def scan_one(path, out_calls, out_pinvokes, out_dynamic, counters):
    name=os.path.basename(path)
    try:
        pe=dnfile.dnPE(path)
        if not getattr(pe,'net',None) or not getattr(pe.net,'mdtables',None):
            counters['non_managed_or_no_metadata']+=1; return
        md=pe.net.mdtables
        methods=getattr(getattr(md,'MethodDef',None),'rows',[]) or []
        implmaps=getattr(getattr(md,'ImplMap',None),'rows',[]) or []
        memberrefs=getattr(getattr(md,'MemberRef',None),'rows',[]) or []
        methodspecs=getattr(getattr(md,'MethodSpec',None),'rows',[]) or []
        owners=build_owner_map(pe)
        pinvoke_by_rid={}
        for ir in implmaps:
            try:
                mf=ir.MemberForwarded
                mr=mf.row
                rid=rid_of(mr)
                if rid:
                    pinvoke_by_rid[rid]={
                        'dll':s(ir.ImportScope.row.Name) if getattr(ir,'ImportScope',None) and getattr(ir.ImportScope,'row',None) else '',
                        'entrypoint':s(ir.ImportName) if getattr(ir,'ImportName',None) else get_name(mr),
                        'managed_method':get_name(mr),
                        'managed_type':owners.get(rid,''),
                    }
            except Exception: counters['implmap_resolution_errors']+=1
        counters['managed_files_scanned']+=1
        counters['methoddefs_seen']+=len(methods)
        counters['pinvoke_declarations_seen']+=len(pinvoke_by_rid)
        # Token lookup for MemberRef and MethodSpec targets.
        for caller_rid,mr in enumerate(methods,1):
            rva=getattr(mr,'Rva',0) or 0
            if not rva: continue
            try:
                body=CilMethodBody(CilMethodBodyReaderBytes(pe.get_data(rva)))
                insns=getattr(body,'instructions',[]) or []
                counters['method_bodies_parsed']+=1
            except Exception:
                counters['method_body_parse_errors']+=1
                continue
            caller_name=get_name(mr)
            caller_type=owners.get(caller_rid,'')
            for ins in insns:
                try: opname=s(ins.opcode.name).lower()
                except Exception: opname=s(getattr(ins,'opcode','')).lower()
                if opname not in CALL_OPS: continue
                tok=token_value(getattr(ins,'operand',None))
                table=table_name(tok) if tok is not None else None
                rid=token_rid(tok) if tok is not None else None
                target_name=''; target_type=''; target_dll=''; target_entry=''; target_kind=''
                if table==0x06 and rid and rid<=len(methods):
                    tr=methods[rid-1]; target_name=get_name(tr); target_type=owners.get(rid,''); target_kind='MethodDef'
                    if rid in pinvoke_by_rid:
                        pi=pinvoke_by_rid[rid]; target_dll=pi['dll']; target_entry=pi['entrypoint']
                elif table==0x0a and rid and rid<=len(memberrefs):
                    tr=memberrefs[rid-1]; target_name=get_name(tr); target_type=member_parent(tr); target_kind='MemberRef'
                elif table==0x2b and rid and rid<=len(methodspecs):
                    tr=methodspecs[rid-1]; target_kind='MethodSpec'
                    try:
                        base=tr.Method.row
                        target_name=get_name(base)
                        target_type=member_parent(base) if hasattr(base,'Class') else ''
                    except Exception: pass
                row={'assembly':name,'caller_type':caller_type,'caller_method':caller_name,
                     'caller_method_rid':caller_rid,'il_offset':getattr(ins,'offset',''),
                     'opcode':opname,'target_token':f'0x{tok:08X}' if tok is not None else '',
                     'target_table':f'0x{table:02X}' if table is not None else '',
                     'target_kind':target_kind,'target_type':target_type,'target_method':target_name,
                     'pinvoke_dll':target_dll,'pinvoke_entrypoint':target_entry}
                out_calls.append(row)
                if target_dll or target_name.lower() in DYNAMIC_NAMES:
                    out_pinvokes.append(row)
                if target_name.lower() in DYNAMIC_NAMES:
                    out_dynamic.append(row)
        # Metadata-only P/Invoke declarations, so declarations lacking visible IL callsites remain explicit.
        for rid,pi in pinvoke_by_rid.items():
            out_pinvokes.append({'assembly':name,'caller_type':pi['managed_type'],'caller_method':pi['managed_method'],
                'caller_method_rid':rid,'il_offset':'','opcode':'DECLARATION_ONLY','target_token':f'0x{(0x06000000 | rid):08X}',
                'target_table':'0x06','target_kind':'MethodDef','target_type':pi['managed_type'],
                'target_method':pi['managed_method'],'pinvoke_dll':pi['dll'],'pinvoke_entrypoint':pi['entrypoint']})
    except Exception as e:
        counters['file_errors']+=1
        print(f'[ERROR] {path}: {type(e).__name__}: {e}',file=sys.stderr)

def write_csv(path, rows):
    if not rows:
        open(path,'w').write('')
        return
    cols=[]
    for r in rows:
        for k in r:
            if k not in cols: cols.append(k)
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore'); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('managed_dir',help='Directory containing original managed .dll files')
    ap.add_argument('-o','--out',default='PINVOKE_STAGE3_OUTPUT')
    args=ap.parse_args()
    files=[]
    for root,_,names in os.walk(args.managed_dir):
        for n in names:
            if n.lower().endswith('.dll'): files.append(os.path.join(root,n))
    files.sort()
    os.makedirs(args.out,exist_ok=True)
    calls=[]; pinvokes=[]; dynamics=[]
    counters=Counter(); counters['dll_files_found']=len(files)
    for i,path in enumerate(files,1):
        scan_one(path,calls,pinvokes,dynamics,counters)
        if i%25==0: print(f'Progress: {i}/{len(files)} DLLs')
    write_csv(os.path.join(args.out,'il_call_sites.csv'),calls)
    write_csv(os.path.join(args.out,'pinvoke_callsite_and_declarations.csv'),pinvokes)
    write_csv(os.path.join(args.out,'dynamic_loader_call_sites.csv'),dynamics)
    # Resolve MemberRef/MethodSpec callsites against P/Invoke declarations by managed type + method.
    decl_index={}
    for d in pinvokes:
        if d.get('opcode')=='DECLARATION_ONLY':
            decl_index.setdefault((d.get('target_type','').lower(),d.get('target_method','').lower()),[]).append(d)
    for row in calls:
        if row.get('target_kind') in ('MemberRef','MethodSpec'):
            matches=decl_index.get((row.get('target_type','').lower(),row.get('target_method','').lower()),[])
            if matches:
                row['pinvoke_dll']=';'.join(sorted({m.get('pinvoke_dll','') for m in matches if m.get('pinvoke_dll')}))
                row['pinvoke_entrypoint']=';'.join(sorted({m.get('pinvoke_entrypoint','') for m in matches if m.get('pinvoke_entrypoint')}))
                row['target_kind'] += '_PInvokeNameMatch'
                pinvokes.append(row)
    counts=Counter(r['opcode'] for r in calls)
    summary={'input_directory':os.path.abspath(args.managed_dir),'dll_files_found':len(files),
      'counters':dict(counters),'call_instruction_rows':len(calls),
      'pinvoke_callsite_and_declaration_rows':len(pinvokes),'dynamic_loader_rows':len(dynamics),
      'opcode_counts':dict(counts),
      'important_limitations':['MemberRef calls are inventoried by metadata token/name; cross-assembly resolution is not guaranteed.',
       'This is static IL evidence, not runtime reachability proof.',
       'Indirect calls, reflection, native callbacks, and computed loader names may require deeper analysis.',
       'A declaration-only row does not mean the P/Invoke is called.']}
    with open(os.path.join(args.out,'stage3_summary.json'),'w') as f: json.dump(summary,f,indent=2)
    print(json.dumps(summary,indent=2))
    print('OUTPUT_DIR='+os.path.abspath(args.out))
    if counters['file_errors'] or counters['method_body_parse_errors']:
        sys.exit(2)
if __name__=='__main__': main()
