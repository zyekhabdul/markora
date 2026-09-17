from markora.cli import main, build_parser


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


def test_cli_prio_and_help(temp_workspace, capsys):
    main(["add", "Task for priority test"])
    capsys.readouterr()

    # Test prio command
    main(["prio", "1", "p2"])
    captured = capsys.readouterr()
    assert "priority set to [P2]" in captured.out

    # Test clearing priority
    main(["prio", "1", "none"])
    captured = capsys.readouterr()
    assert "priority set to [NONE]" in captured.out

    # Test help command
    main(["help"])
    captured = capsys.readouterr()
    assert "Markora v" in captured.out
    assert "TODO COMMANDS:" in captured.out

