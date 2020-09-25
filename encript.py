from urllib import parse

if __name__ == '__main__':
    a = 'https://amoker.com/'

    print(parse.quote_from_bytes(a))