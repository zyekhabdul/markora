from markora.cli import main, build_parser


def test_cli_short_aliases(temp_workspace, capsys):
    main(["a", "Short alias task", "-p", "p2"])
    captured = capsys.readouterr()
    assert "[ OK ] Added task" in captured.out

    main(["ls"])
    captured = capsys.readouterr()
    assert "Short alias task" in captured.out
    assert "[P2]" in captured.out

    main(["qn", "Short qn note"])
    captured = capsys.readouterr()
    assert "Appended to QuickNote" in captured.out


def test_cli_default_fallback(temp_workspace, capsys):
    # Without args in non-tty environment, falls back to list
    main([])
    captured = capsys.readouterr()
    assert "MASTER TODOLIST" in captured.out
