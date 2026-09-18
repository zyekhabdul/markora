# Bash completion for markora
_markora_completions() {
    local cur prev subcommands
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    subcommands="quicknote qn list ls add a done do undone undo toggle x rm edit e note n notes nl find search rename mv ui gui keep fav"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${subcommands} -h --help -v --version" -- "${cur}") )
        return 0
    fi

    case "${prev}" in
        add|a)
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "-p --prio -s --section --help" -- "${cur}") )
            fi
            ;;
        list|ls)
            COMPREPLY=( $(compgen -W "-p --pending -d --done -t --tag -s --section -c --compact" -- "${cur}") )
            ;;
        keep)
            COMPREPLY=( $(compgen -W "auth status pull push sync logout --manual" -- "${cur}") )
            ;;
        fav)
            COMPREPLY=( $(compgen -W "list ls add rm remove toggle" -- "${cur}") )
            ;;
    esac
}

complete -F _markora_completions markora
complete -F _markora_completions td
