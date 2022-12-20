

def validate_integer(value):
    try:
        value = int(value)
    except ValueError:
        value = False
    return value