import os
from td.quicknote import load_quicknote, append_quicknote


def test_quicknote_flow(temp_workspace):
    qn_file = temp_workspace["quicknote_file"]
    assert not os.path.exists(qn_file)

    # Initial load creates scaffold
    lines = load_quicknote(qn_file)
    assert os.path.exists(qn_file)
    assert any("QUICKNOTE" in l for l in lines)

    # Append entry
    entry = append_quicknote("Remember to deploy update", qn_file)
    assert "Remember to deploy update" in entry

    lines_after = load_quicknote(qn_file)
    assert any("Remember to deploy update" in l for l in lines_after)
