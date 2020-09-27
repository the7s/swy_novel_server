

def encrypt(string):
    return string.replace('/', '^').replace('.', '*')


def decrypt(string):
    return string.replace('^', '/').replace('*', '.')
