from checkers.disallowed_characters import disallowed


def name_length(string: str):
    _string = disallowed(string)
    maximum_length = 30
    if len(_string) > maximum_length:
        return _string[:maximum_length]
    else:
        return _string
