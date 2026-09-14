from backend.config import format_model_input, VALID_REGIONS, normalize_bengali_text

def test_valid_regions_count():
    assert len(VALID_REGIONS) == 7
    expected = ["Pabna", "Noakhali", "Jashore", "Rangpur", "Mymensingh", "Barishal", "Chittagong"]
    for reg in expected:
        assert reg in VALID_REGIONS

def test_format_model_input():
    result = format_model_input("Chittagong", "ক্যান আছু?")
    assert result == "translate Chittagong to Bangla: ক্যান আছু?"

def test_format_model_input_cleaning():
    # Extra whitespace and newline
    result = format_model_input("Noakhali", "  তুই   কই যাস?  \n ")
    assert result == "translate Noakhali to Bangla: তুই কই যাস?"

def test_normalize_bengali_text():
    raw = "মুই বাড়িত যামু\u200B"
    cleaned = normalize_bengali_text(raw)
    assert "\u200B" not in cleaned
