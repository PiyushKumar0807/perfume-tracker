import requests
s = requests.Session()
# login
r = s.post('http://localhost:5000/login', data={'username':'testuser1', 'password':'testpass'}, allow_redirects=True)
print('login', r.status_code)
# fetch perfumes
r2 = s.get('http://localhost:5000/perfumes')
print('perfumes', r2.status_code)
print(r2.text[:300])
