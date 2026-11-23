from types import SimpleNamespace
from job_intelligence.models import Job
from job_intelligence import sheets

class WS:
 def __init__(self,values=None): self.values=values or []; self.inserted=[]; self.cleared=False
 def get_all_values(self): return [list(r) for r in self.values]
 def append_row(self,row): self.values.append(list(row))
 def append_rows(self,rows): self.values.extend([list(r) for r in rows])
 def insert_row(self,row,index): self.values.insert(index-1,list(row)); self.inserted.append(index)
 def clear(self): self.values=[]; self.cleared=True
 def update(self,cell,rows):
  assert cell=="A2"; self.values=self.values[:1]+[list(r) for r in rows]
 def get_all_records(self):
  header=self.values[0]; return [dict(zip(header,row)) for row in self.values[1:]]
class Book:
 def __init__(self,master): self.tabs={name:(master if name=="All Jobs" else WS()) for name in sheets.TABS}
 def worksheet(self,name): return self.tabs[name]
 def add_worksheet(self,name,rows,cols): self.tabs[name]=WS(); return self.tabs[name]
def test_empty_worksheet_gets_header():
 ws=WS(); assert sheets.ensure_headers(ws,sheets.headers())=="empty"; assert ws.values[0]==sheets.headers()
def test_headerless_data_is_shifted_not_destroyed():
 ws=WS([["legacy","data"]]); assert sheets.ensure_headers(ws,sheets.headers())=="repaired"; assert ws.values[1]==["legacy","data"] and ws.inserted==[1]
def test_existing_correct_header_is_unchanged():
 ws=WS([sheets.headers(),["id"]]); assert sheets.ensure_headers(ws,sheets.headers())=="valid"; assert ws.inserted==[]
def test_update_preserves_manual_fields(monkeypatch):
 header=sheets.headers(); old={h:"" for h in header}; old.update({"Internal Job ID":"id1","Application Status":"Applied","Notes":"keep","Follow-up Date":"2026-12-01","First Seen Date":"2026-01-01"})
 master=WS([header,[old[h] for h in header]]); book=Book(master); monkeypatch.setattr(sheets,"_client",lambda settings:book)
 settings=SimpleNamespace(sheet_id="test",service_account_b64="x",company_evidence={})
 job=Job("orig","Business Analyst","Co","test","https://x",internal_id="id1",location="India")
 sheets.update(settings,[job],[]); row=dict(zip(header,master.values[1])); assert row["Application Status"]=="Applied" and row["Notes"]=="keep" and row["Follow-up Date"]=="2026-12-01" and row["First Seen Date"]=="2026-01-01"
