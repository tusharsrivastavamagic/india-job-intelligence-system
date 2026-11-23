from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from job_intelligence.connectors.apify import TokenManager,fetch_apify

def test_token_manager_trims_empty_and_rotates():
 manager=TokenManager([" one ","","two","  ","three"])
 assert manager.count==3 and [manager.acquire() for _ in range(4)]==["one","two","three","one"]
def test_token_manager_supports_many_tokens():
 tokens=[f"token-{n}" for n in range(12)]; manager=TokenManager(tokens)
 assert [manager.acquire() for _ in tokens]==tokens
def test_unavailable_token_is_skipped():
 manager=TokenManager(["one","two"]); manager.mark_unavailable("one")
 assert manager.acquire()=="two" and manager.acquire()=="two"
def test_concurrent_acquisition_has_no_missing_token():
 manager=TokenManager(["one","two","three"])
 with ThreadPoolExecutor(max_workers=12) as pool: results=list(pool.map(lambda _:manager.acquire(),range(60)))
 assert set(results)=={"one","two","three"} and None not in results
def settings(tokens=("one",),legacy="",enabled=None):
 return SimpleNamespace(apify_tokens=tokens,apify_token=legacy,apify_enabled=enabled or {"naukri":True},apify_actor_inputs={},apify_max_items=2)
class HTTPError(Exception):
 def __init__(self,status): self.response=SimpleNamespace(status_code=status); super().__init__(f"HTTP {status}")
def client_factory(outcomes, seen):
 def factory(token):
  seen.append(token)
  class Dataset:
   def list_items(self,limit):
    value=outcomes[token]
    if isinstance(value,Exception): raise value
    return SimpleNamespace(items=value)
  class Actor:
   def call(self,run_input): return {"defaultDatasetId":"d"}
  class Client:
   def actor(self,name): return Actor()
   def dataset(self,id): return Dataset()
  return Client()
 return factory
def test_rate_limit_switches_without_leaking_token_in_errors():
 seen=[]; jobs,errors=fetch_apify(settings(("secret-one","secret-two")),client_factory({"secret-one":HTTPError(429),"secret-two":[{"title":"Analyst","company":"Co","url":"https://x"}]},seen))
 assert seen==["secret-one","secret-two"] and len(jobs)==1 and not any("secret" in err for err in errors)
def test_auth_failure_switches_token():
 seen=[]; jobs,_=fetch_apify(settings(("first","second")),client_factory({"first":HTTPError(401),"second":[{"title":"Analyst","company":"Co","url":"https://x"}]},seen))
 assert seen==["first","second"] and jobs
def test_exhaustion_stops_after_each_token():
 seen=[]; _,errors=fetch_apify(settings(("one","two")),client_factory({"one":HTTPError(429),"two":HTTPError(503)},seen))
 assert seen==["one","two"] and "no available token" in errors[0]
def test_legacy_token_fallback_works():
 seen=[]; jobs,_=fetch_apify(settings((),"legacy"),client_factory({"legacy":[{"title":"Analyst","company":"Co","url":"https://x"}]},seen))
 assert seen==["legacy"] and jobs
