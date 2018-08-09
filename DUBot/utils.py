cmds = {
    "help" : {
        "mod" : False,
        "example" : "[command]",
        "desc" : "Type $help <command> to see a description of some command, or type $all to see a list of all commands. If any command argument includes whitespace, enclose that argument in \"quotation marks like this\".\nHint: you can type bank account IDs without leading zeros and without spaces, so `0000 0045` can be written as `45`.",
        "alias" : [ "?" ]
    }
}

def get_alias(cmd):
    """ Returns the command that this command is an alias of [e.g. the command that has the string {cmd} in its {alias} list] """
    for command in cmds:
        if cmd.lower() == command.lower(): return command

        if not "alias" in cmds[command]: continue

        for alias in cmds[command]["alias"]:
            if alias.lower() == cmd.lower(): return command

    return None

def get_help(cmd, is_owner = False):
    """ Returns the description of this command. """
    cmd = cmd.replace('$', '')
    main = get_alias(cmd)
    
    if main is None: return 'Unknown command ${0:s}'.format(cmd)

    tag = cmds[main]

    if "mod" in tag:
        if tag["mod"] and not is_owner:
            return 'Unknown command ${0:s}'.format(cmd)

    res = '${0:s}\n{1:s}'.format(main, cmds[main]['desc'])

    if 'example' in tag:
        res += '\n\nExample: ${0:s} {1:s}'.format(main, cmds[main]['example'])

    if 'alias' in tag:
        res += '\n\nAliases: ' + ', '.join(tag['alias'])

    return '```' + res + '```'