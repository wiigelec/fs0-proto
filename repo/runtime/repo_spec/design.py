from __future__ import annotations
from dataclasses import dataclass
import re
from .errors import DesignError

_DOC_ID = re.compile(r"^DP-[0-9]{3}$")
_STMT = re.compile(r"^\*\*(DP[0-9]{3}-[A-Z0-9-]+-[0-9]{3})\*\*\s*$")

@dataclass(frozen=True)
class StatementAddress:
    statement_id: str
    line: int

@dataclass(frozen=True)
class DesignProposal:
    doc_id: str
    path: str
    revision: str
    artifact_type: str
    canonical_format: str
    depends_on: tuple[str,...]
    statements: tuple[StatementAddress,...]
    def statement_ids(self): return {s.statement_id for s in self.statements}

@dataclass(frozen=True)
class DesignIndex:
    proposals: tuple[DesignProposal,...]
    def by_doc_id(self): return {p.doc_id:p for p in self.proposals}

def _scalar(v):
    v=v.strip()
    if v=="[]": return []
    if v.startswith("[") and v.endswith("]"):
        x=v[1:-1].strip()
        return [] if not x else [i.strip().strip("'\"") for i in x.split(",")]
    return v.strip("'\"")

def _front(text):
    lines=text.splitlines()
    if not lines or lines[0].strip()!="---":
        raise DesignError("missing-metadata-header","Design Proposal must begin with ---")
    meta={}
    pending_list_key=None
    for n,line in enumerate(lines[1:],2):
        if line.strip()=="---":
            return meta
        if not line.strip():
            continue
        if line[:1].isspace():
            stripped=line.strip()
            if pending_list_key is None or not stripped.startswith("- "):
                raise DesignError("invalid-metadata-line",f"invalid metadata line {n}")
            item=stripped[2:].strip()
            if not item:
                raise DesignError("invalid-metadata-line",f"empty metadata list item at line {n}")
            meta[pending_list_key].append(_scalar(item))
            continue
        pending_list_key=None
        if ":" not in line:
            raise DesignError("invalid-metadata-line",f"invalid metadata line {n}")
        k,v=line.split(":",1)
        k=k.strip()
        if k in meta:
            raise DesignError("duplicate-metadata-key",f"duplicate metadata key: {k}")
        if not v.strip():
            meta[k]=[]
            pending_list_key=k
        else:
            meta[k]=_scalar(v)
    raise DesignError("unterminated-metadata-header","metadata header not terminated")

def parse_design(text, *, path, revision):
    m=_front(text); doc_id=str(m.get("doc_id",""))
    if not _DOC_ID.fullmatch(doc_id): raise DesignError("invalid-doc-id",f"invalid doc_id {doc_id!r}",path=path)
    if m.get("artifact_type")!="design-proposal": raise DesignError("invalid-artifact-type","artifact_type must be design-proposal",path=path)
    if m.get("canonical_format")!="markdown": raise DesignError("invalid-canonical-format","canonical_format must be markdown",path=path)
    raw=m.get("depends_on",[]); deps=tuple(str(x) for x in raw) if isinstance(raw,list) else ((str(raw),) if raw else ())
    seen=set(); addrs=[]; prefix=doc_id.replace("-","")+"-"
    for n,line in enumerate(text.splitlines(),1):
        mt=_STMT.match(line.strip())
        if not mt: continue
        sid=mt.group(1)
        if not sid.startswith(prefix): raise DesignError("foreign-statement-id",f"{sid} does not belong to {doc_id}",path=path)
        if sid in seen: raise DesignError("duplicate-statement-id",f"duplicate statement ID {sid}",path=path)
        seen.add(sid); addrs.append(StatementAddress(sid,n))
    return DesignProposal(doc_id,path,revision,"design-proposal","markdown",deps,tuple(addrs))

def load_design_input(repository, design_input):
    for k in ("doc_id","path","revision","statements"):
        if k not in design_input: raise DesignError("missing-design-input-field",f"missing field {k}")
    p=parse_design(repository.read_text_at(design_input["revision"],design_input["path"]),
                   path=design_input["path"],revision=design_input["revision"])
    if p.doc_id!=design_input["doc_id"]: raise DesignError("design-doc-id-mismatch",f"expected {design_input['doc_id']}, found {p.doc_id}")
    selected=design_input["statements"]
    if not isinstance(selected,list) or not selected or len(selected)!=len(set(selected)):
        raise DesignError("invalid-selected-statements","selected statements must be unique and non-empty")
    missing=[x for x in selected if x not in p.statement_ids()]
    if missing: raise DesignError("unresolved-selected-statement",f"selected statements not found: {missing}",path=p.path)
    return p

def resolve_design_inputs(repository, design_inputs):
    ps=tuple(load_design_input(repository,d) for d in design_inputs); by={p.doc_id:p for p in ps}
    if len(by)!=len(ps): raise DesignError("duplicate-design-input","duplicate Design Proposal input")
    for p in ps:
        for dep in p.depends_on:
            if dep and dep not in by: raise DesignError("unresolved-design-dependency",f"{p.doc_id} depends on undeclared {dep}")
    return DesignIndex(ps)
