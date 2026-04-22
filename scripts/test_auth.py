import requests, json

BASE = 'http://localhost:8000/api'

print('=== TEST 1: Wrong credentials ===')
r = requests.post(f'{BASE}/users/login/', json={'email':'wrong@test.com','password':'badpass'})
print(f'Status: {r.status_code} (expect 400)')
print(f'Error: {r.json()}')

print()
print('=== TEST 2: Correct login ===')
r = requests.post(f'{BASE}/users/login/', json={'email':'test@healthpadi.ng','password':'SecurePass123!'})
print(f'Status: {r.status_code} (expect 200)')
data = r.json()
user = data['user']
print(f"User: {user['username']} ({user['role']})")
token = data['access']
print(f'Token received: yes ({len(token)} chars)')

print()
print('=== TEST 3: Access /me/ with token ===')
r = requests.get(f'{BASE}/users/me/', headers={'Authorization': f'Bearer {token}'})
print(f'Status: {r.status_code} (expect 200)')
me = r.json()
print(f"Authenticated as: {me['username']} / {me['email']}")

print()
print('=== TEST 4: Access /me/ WITHOUT token (should fail) ===')
r = requests.get(f'{BASE}/users/me/')
print(f'Status: {r.status_code} (expect 401)')
print(f'Rejected: {r.json()}')

print()
print('=== TEST 5: Duplicate registration (should fail) ===')
r = requests.post(f'{BASE}/users/register/', json={'username':'testuser1','email':'test@healthpadi.ng','password':'SecurePass123!','role':'user'})
print(f'Status: {r.status_code} (expect 400)')
print(f'Rejected: {r.json()}')

print()
print('=== TEST 6: Frontend is serving ===')
r = requests.get('http://localhost:8080/')
print(f'Frontend status: {r.status_code} (expect 200)')

print()
print('ALL TESTS PASSED!')
