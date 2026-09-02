import os
from td.favorites import FavoritesManager


def test_favorites_manager(temp_workspace):
    fav_file = temp_workspace["fav_file"]
    docs_dir = temp_workspace["docs_dir"]
    fm = FavoritesManager(filepath=fav_file, docs_dir=docs_dir)

    test_note = os.path.join(docs_dir, "notes", "architecture.md")
    with open(test_note, "w") as f:
        f.write("# Architecture Note\n")

    rel_path = "notes/architecture.md"

    assert not fm.is_favorite(rel_path)

    # Toggle add
    is_fav, msg = fm.toggle(test_note)
    assert is_fav
    assert fm.is_favorite(rel_path)

    # Check persistence
    fm2 = FavoritesManager(filepath=fav_file, docs_dir=docs_dir)
    assert fm2.is_favorite(rel_path)
    fav_list = fm2.get_favorites()
    assert len(fav_list) == 1
    assert fav_list[0][0] == rel_path

    # Toggle remove
    is_fav, msg = fm2.toggle(test_note)
    assert not is_fav
    assert not fm2.is_favorite(rel_path)
