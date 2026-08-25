from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
from .design import DesignIndex, resolve_design_inputs
from .errors import PlanningError
from .jsonio import load_json, normalize_repo_path, require_sha40

_FS_ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_DOC_ID=re.compile(r"^DP-[0-9]{3}$")
_STMT=re.compile(r"^DP[0-9]{3}-[A-Z0-9-]+-[0-9]{3}$")

@dataclass(frozen=True)
class FunctionalSet:
    order:int; id:str; kind:str; title:str; description:str
    accepted_predecessor:str; design_inputs:tuple[dict,...]; design_index:DesignIndex

def _exact(obj, allowed, where):
    extra=set(obj)-allowed
    if extra: raise PlanningError("unexpected-field",f"{where} contains unexpected fields: {sorted(extra)}")

def load_functional_set(path, repository):
    path=Path(path); doc=load_json(path)
    if not isinstance(doc,dict): raise PlanningError("invalid-functional-set","root must be object")
    _exact(doc,{"schema_version","artifact_type","functional_set","accepted_predecessor","design_inputs"},"functional-set")
    if doc.get("schema_version")!="1" or doc.get("artifact_type")!="functional-set":
        raise PlanningError("invalid-functional-set-header","unsupported schema_version/artifact_type")
    fs=doc.get("functional_set")
    if not isinstance(fs,dict): raise PlanningError("invalid-functional-set-identity","functional_set must be object")
    _exact(fs,{"order","id","kind","title","description"},"functional_set")
    order,fsid,kind=fs.get("order"),fs.get("id"),fs.get("kind")
    if not isinstance(order,int) or order<0: raise PlanningError("invalid-functional-set-order","order must be non-negative")
    if not isinstance(fsid,str) or not _FS_ID.fullmatch(fsid): raise PlanningError("invalid-functional-set-id","invalid id")
    if kind not in {"core","extension"}: raise PlanningError("invalid-functional-set-kind","kind must be core or extension")
    pred=doc.get("accepted_predecessor")
    if not isinstance(pred,dict) or set(pred)!={"repository_revision"}: raise PlanningError("invalid-accepted-predecessor","invalid predecessor object")
    predecessor=require_sha40(pred["repository_revision"],field="accepted_predecessor.repository_revision")
    repository.require_revision(predecessor)
    inputs=doc.get("design_inputs")
    if not isinstance(inputs,list) or not inputs: raise PlanningError("invalid-design-inputs","design_inputs must be non-empty")
    norm=[]; seen=set()
    for i,item in enumerate(inputs):
        if not isinstance(item,dict): raise PlanningError("invalid-design-input",f"design_inputs[{i}] must be object")
        _exact(item,{"doc_id","path","revision","statements"},f"design_inputs[{i}]")
        did=item.get("doc_id")
        if not isinstance(did,str) or not _DOC_ID.fullmatch(did) or did in seen: raise PlanningError("invalid-design-doc-id",f"invalid/duplicate doc_id at {i}")
        seen.add(did); p=normalize_repo_path(item.get("path",""))
        if not p.startswith("repo/proposals/") or not p.endswith(".md"): raise PlanningError("invalid-design-path",f"invalid Design path {p}")
        rev=require_sha40(item.get("revision",""),field=f"design_inputs[{i}].revision")
        st=item.get("statements")
        if not isinstance(st,list) or not st or len(st)!=len(set(st)): raise PlanningError("invalid-design-statements",f"invalid statements at {i}")
        if any(not isinstance(s,str) or not _STMT.fullmatch(s) for s in st): raise PlanningError("invalid-design-statement-id",f"invalid statement ID at {i}")
        norm.append({"doc_id":did,"path":p,"revision":rev,"statements":list(st)})
    idx=resolve_design_inputs(repository,norm)
    return FunctionalSet(order,fsid,kind,fs["title"],fs["description"],predecessor,tuple(norm),idx)
