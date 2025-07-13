with open('my_file.txt', 'w+') as f:
    f.write('hello')
    f.seek(0)
    content = f.read()
    f.write(content.upper())