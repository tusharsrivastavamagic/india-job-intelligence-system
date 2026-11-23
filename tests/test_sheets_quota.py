from job_intelligence import sheets
class Response: status_code=429
class QuotaError(Exception): response=Response()
def test_429_retries_with_backoff(monkeypatch):
 calls=[]; sleeps=[]
 def operation():
  calls.append(1)
  if len(calls)<3: raise QuotaError("quota exceeded")
  return "ok"
 monkeypatch.setattr(sheets.time,"sleep",lambda seconds:sleeps.append(seconds))
 assert sheets.api_call(operation)=="ok" and len(calls)==3 and sleeps==[1,2]
def test_batch_values_uses_one_api_call():
 class Book:
  def __init__(self):self.calls=0
  def values_batch_get(self,ranges):
   self.calls+=1;return {"valueRanges":[{"values":[[name]]} for name in ["All Jobs","New Today"]]}
 book=Book(); values=sheets._batch_values(book,["All Jobs","New Today"])
 assert book.calls==1 and values["All Jobs"]==[["All Jobs"]] and values["New Today"]==[["New Today"]]
