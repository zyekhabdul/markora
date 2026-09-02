# Bash completion for markora
_markora_completions() {
    local cur prev subcommands
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    subcommands="quicknote qn scratch list ls todo add a done do check undone undo uncheck toggle x rm del remove edit e note n notes nl find search grep rename mv ui tui dui app gui keep gk gkeep fav favorite pin star"

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
        list|ls|todo)
            COMPREPLY=( $(compgen -W "-p --pending -d --done -t --tag -s --section -c --compact" -- "${cur}") )
            ;;
        keep|gk|gkeep)
            COMPREPLY=( $(compgen -W "auth status pull push sync logout --manual" -- "${cur}") )
            ;;
        fav|favorite|pin|star)
            COMPREPLY=( $(compgen -W "list ls add rm remove toggle" -- "${cur}") )
            ;;
    esac
}

complete -F _markora_completions markora
complete -F _markora_completions td
complete -F _markora_completions todo
complete -F _markora_completions mo
