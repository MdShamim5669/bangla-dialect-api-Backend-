import pytest
from backend.hf_client import get_simulated_translation, query_translation

def test_get_simulated_translation():
    res = get_simulated_translation("Chittagong", "ক্যান আছু?")
    assert "কেমন" in res

    res2 = get_simulated_translation("Barishal", "মুই বাড়িত যামু")
    assert "বাড়ি" in res2

    res3 = get_simulated_translation("Noakhali", "তুই কই যাস?")
    assert "কোথায়" in res3

@pytest.mark.anyio
async def test_query_translation_simulation_mode():
    result = await query_translation(
        region="Chittagong",
        sentence="ক্যান আছু?",
        custom_repo_id="your-username/banglat5-dialect-to-standard",
        custom_token="",
    )
    assert result["success"] is True
    assert result["mode"] == "simulation"
    assert "translation" in result
    assert result["prompt_used"] == "translate Chittagong to Bangla: ক্যান আছু?"
