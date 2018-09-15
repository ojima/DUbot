cmds = {
    "help" : {
        "limit" : None,
        "example" : "[command]",
        "desc" : "Type $help <command> to see a description of some command, or type $all to see a list of all commands. If any command argument includes whitespace, enclose that argument in \"quotation marks like this\".\nHint: you can type bank account IDs without leading zeros and without spaces, so `0000 0045` can be written as `45`.",
        "alias" : [ "?" ]
    },
    "all" : {
        "limit" : None,
        "desc" : "List all commands you have access to."
    },
    "settings" : {
        "limit" : [ "operator" ],
        "example" : "[set <name> <value>]",
        "desc" : "View or change settings of DUBot."
    },
    "roles" : {
        "limit" : None,
        "example" : "[player]",
        "desc" : "Shows the roles of a player and when its terms run out. If no player is provided it shows your roles.",
        "alias" : [ "terms" ]
    },
    "addrole" : {
        "limit" : [ "operator" ],
        "example" : "<player> <role> [end]",
        "desc" : "Give a role to a player. The end date is asserted to be of the format DD-MM-YYYY. If no end date is provided, the role is assumed to be indefinite.",
    },
    "delrole" : {
        "limit" : [ "operator" ],
        "example" : "<player> <role>",
        "desc" : "Take away a role from a player."
    },
    "save" : {
        "limit" : [ "operator" ],
        "desc" : "Force a full data save.",
        "alias" : [ "saveall", "dump" ]
    },
    "stop" : {
        "limit" : [ "operator" ],
        "desc" : "Gracefully stop the bot, executing a full save and all."
    },
    "kill" : {
        "limit" : [ "operator" ],
        "desc" : "Force stop the bot, without saving data."
    },
    "newaccount" : {
        "limit" : None,
        "example" : "<name>",
        "desc" : "Register a new bank account on your name.",
        "alias" : [ "register" ]
    },
    "balance" : {
        "limit" : None,
        "desc" : "Display your total banking balance.",
        "alias" : [ "accounts" ]
    },
    "transfer" : {
        "limit" : None,
        "example" : "<from> <to> <amount> [comment]",
        "desc" : "Transfer money from your bank account to a different bank account."
    },
    "reactboard" : {
        "limit" : [ "operator", "moderator" ],
        "example" : "<channel> [remove/limit [lim]]",
        "desc" : "Sets a reaction channel. Secondary command [remove] removes given channel as react board. Command [limit] sets the minimum limit to [lim] (default = 3, max = 25)."
    },
}

def get_alias(cmd):
    """ Returns the command that this command is an alias of [e.g. the command that has the string {cmd} in its {alias} list] """
    for command in cmds:
        if cmd.lower() == command.lower(): return command

        if not "alias" in cmds[command]: continue

        for alias in cmds[command]["alias"]:
            if alias.lower() == cmd.lower(): return command

    return None

def can_do(cmd, roles = None):
    """ Returns whether a collection of roles give the person permission to execute this command """
    tag = cmds[cmd]
    if tag['limit'] is None:
        return True

    if roles is None:
        return False

    for role in roles:
        if role.name in tag['limit']:
            return True

    return False

def get_help(cmd, roles = None):
    """ Returns the description of this command. """
    cmd = cmd.replace('$', '')
    main = get_alias(cmd)

    if main is None: return 'Unknown command ${0:s}'.format(cmd)

    tag = cmds[main]

    if not can_do(cmd, roles):
        return 'Unknown command ${0:s}'.format(cmd)

    res = '${0:s}\n{1:s}'.format(main, cmds[main]['desc'])

    if 'example' in tag:
        res += '\n\nExample: ${0:s} {1:s}'.format(main, cmds[main]['example'])

    if 'alias' in tag:
        res += '\n\nAliases: ' + ', '.join(tag['alias'])

    return '```' + res + '```'

# returns a quick list of all commands
def get_all(roles = None):
    res = '```'
    i = 1
    for cmd in cmds:
        if not can_do(cmd, roles): continue

        res += '{2:2d}. {0:s}: {1:s}\n'.format(cmd, cmds[cmd]['desc'], i)
        i += 1

    return res.strip() + '```'

# retardifies a string - giving it stupid/ridiculous symbols.
def retardify(string):
    result = string
    
    result = list(result)
    
    slike = [ u'\u017F', u's', u'S' ]
    roundl = [ 'o', 'b', 'p', 'h', u'\u01BF', u'\u00FE' ]
    
    for i, s in enumerate(result):
        if s == 's':
            if i+1 == len(result) or not result[i+1].isalpha(): pass
            elif i == 0: result[i] = u'\u017F'
            elif not result[i-1] in slike: result[i] = u'\u017F'
    
    for i, r in enumerate(result):
        if r == 'r' and i > 0 and result[i-1] in roundl: result[i] = u'\uA75B'
    
    result = ''.join(result)
    
    result = result.replace('et', u'\u204A') # Tyronian et
    result = result.replace('w', u'\u01BF').replace('W', u'\u01F7') # Wynn
    result = result.replace('th', u'\u00FE').replace('Th', u'\u00DE').replace('TH', u'\u00DE') # Thorn
    
    return result

# de-retardifies a string
def detardify(string):
    string = string.replace(u'\u017F', 's') # Long s
    string = string.replace(u'\u204A', 'et') # Tyronian et
    string = string.replace(u'\uA75B', 'r') # R rotunda
    string = string.replace(u'\u01BF', 'w') # Lower-case wynn
    string = string.replace(u'\u01F7', 'W') # Upper-case Wynn
    string = string.replace(u'\u00FE', 'th') # Lower-case thorn
    string = string.replace(u'\u00DE', 'Th') # Upper-case thorn
    
    return string