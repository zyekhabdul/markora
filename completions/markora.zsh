#compdef markora td
 
_markora() {
    local -a subcommands
    subcommands=(
        'ui:Launch interactive 4-tab Curses TUI (default)'
        'quicknote:Append or view QuickNotes (alias: qn)'
        'qn:Append or view QuickNotes'
        'list:List todos with status, priority, and tags (alias: ls)'
        'ls:List todos'
        'add:Add a new task (alias: a)'
        'a:Add a new task'
        'done:Mark task(s) as completed (alias: do)'
        'do:Mark task(s) as completed'
        'undone:Mark task(s) as pending (alias: undo)'
        'undo:Mark task(s) as pending'
        'toggle:Toggle task(s) completion status (alias: x)'
        'x:Toggle task(s) completion status'
        'rm:Delete task(s)'
        'note:Create or edit a markdown note (alias: n)'
        'n:Create or edit a markdown note'
        'notes:List all notes in notebook (alias: nl)'
        'nl:List all notes in notebook'
        'find:Search across all notes & todos (alias: search)'
        'search:Search across all notes & todos'
        'rename:Rename task, note, or folder (alias: mv)'
        'mv:Rename task, note, or folder'
        'fav:Manage favorite and pinned notes'
        'keep:Google Keep sync & integration'
        'edit:Open todolist in $EDITOR (alias: e)'
        'e:Open todolist in $EDITOR'
        'gui:Launch in desktop terminal window'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands "markora subcommands" subcommands
    fi
}

_markora "$@"
