from types import SimpleNamespace
import pytest
from job_intelligence.gemini import test_ai as run_ai_test
def test_ai_requires_explicit_enable():
 with pytest.raises(ValueError): run_ai_test(SimpleNamespace(gemini_enabled=False,gemini_api_key="",gemini_model="x"))
