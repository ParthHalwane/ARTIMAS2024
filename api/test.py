from github import Github

g = Github('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')

repo = g.get_repo('Prathmesh-Kolekar/Artimas24')

with open(r'C:\Users\Prathmesh\Downloads\068a13d9-5f81-4cdc-9270-311def6046bb.jpg', 'rb') as file:
    data = file.read()

repo.create_file('data/temp.jpg', 'upload csv', data, branch='main')