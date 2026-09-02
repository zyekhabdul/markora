from td.cli import main, build_parser


def test_build_parser():
    parser = build_parser()
    args = parser.parse_args(["add", "Test", "task", "-p", "p1"])
    assert args.command == "add"
    assert args.title == ["Test", "task"]
    assert args.prio == "p1"


def test_cli_execution_add_and_list(temp_workspace, capsys):
    main(["add", "Integration", "test", "task", "-p", "p1"])
    captured = capsys.readouterr()
    assert "[ OK ] Added task" in captured.out

    main(["list"])
    captured = capsys.readouterr()
    assert "Integration test task" in captured.out
    assert "[P1]" in captured.out


def test_cli_quicknote(temp_workspace, capsys):
    main(["quicknote", "Testing quicknote from CLI"])
    captured = capsys.readouterr()
    assert "Appended to QuickNote" in captured.out
