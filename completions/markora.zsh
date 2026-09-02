#compdef markora td todo mo

_markora() {
    local -a subcommands
    subcommands=(
        'ui:Launch interactive 4-tab Curses TUI'
        'quicknote:Append or view QuickNotes (quicknote.md)'
        'list:List todos with status, priority, and tags'
        'add:Add a new task'
        'done:Mark task(s) as completed'
        'undone:Mark task(s) as pending'
        'toggle:Toggle task(s) completion status'
        'rm:Delete task(s)'
        'note:Create or edit a markdown note'
        'notes:List all notes in notebook'
        'find:Search across all notes & todos'
        'rename:Rename task, note, or folder'
        'fav:Manage favorite and pinned notes'
        'keep:Google Keep sync & integration'
        'edit:Open todolist in $EDITOR'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands "markora subcommands" subcommands
    fi
}

_markora "$@"
