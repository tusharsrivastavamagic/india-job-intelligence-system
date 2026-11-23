from job_intelligence.models import Job
from job_intelligence.dedupe import deduplicate
def test_merges_source_urls():
    a=Job("a","Business Analyst","Co","greenhouse","https://apply.example/a",direct_apply_url="https://apply.example/a")
    b=Job("b","Business Analyst","Co","lever","https://apply.example/a",direct_apply_url="https://apply.example/a")
    result=deduplicate([a,b]); assert len(result)==1 and "lever" in result[0].source
