import requests
s = requests.Session()
print('index', s.get('http://localhost:5000').status_code)
# register user (if already exists, skip)
for u in ['testuser1', 'testuser2']:
    r = s.post('http://localhost:5000/register', data={'username':u, 'email':f'{u}@example.com', 'password':'testpass', 'confirm_password':'testpass'})
    print(f'register {u}', r.status_code)
    if r.status_code in [302, 200]:
        if r.history:
            print('   redirected to', r.url)

r = s.post('http://localhost:5000/login', data={'username':'testuser1', 'password':'testpass'}, allow_redirects=False)
print('login', r.status_code, r.headers.get('Location'))
if r.status_code == 302:
    dash = s.get('http://localhost:5000' + r.headers['Location'])
    print('dashboard', dash.status_code)
    print('dashboard snippet:', dash.text[:400])
