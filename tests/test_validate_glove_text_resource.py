from pathlib import Path
def test_validator_is_pickle_free():
    text=(Path(__file__).parents[1]/"scripts"/"validate_glove_text_resource.py").read_text()
    assert "pickle.load" not in text and "allow_pickle=False" in text
