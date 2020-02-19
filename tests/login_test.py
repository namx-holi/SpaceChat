from test_client import make_request

# TODO: Add invalid logins or missing params

print("Running login_test\n")

print("Register a new user")
resp = make_request("register", {"username":"Bepis", "password":"swag"})

print("Try register that user again")
resp = make_request("register", {"username":"Bepis", "password":"swag"})
assert resp == dict(error="user 'Bepis' already exists")

print("Try log in with wrong password")
resp = make_request("login", {"username":"Bepis", "password":"swagh"})
assert resp == dict(error="incorrect password")

print("Try log in with correct password")
resp = make_request("login", {"username":"Bepis", "password":"swag"})
assert resp["msg"] == "user 'Bepis' logged in"
token = resp["token"]

print("Try log in while already logged in")
resp = make_request("login", {"username":"Bepis", "password":"swag"})
assert resp["msg"] == "user 'Bepis' logged in"
token2 = resp["token"]

assert token != token2 # Make sure tokens are different

print("Try log out")
resp = make_request("logout", {"token":token2})
assert resp == dict(msg="logged out")
