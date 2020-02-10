from test_client import make_request

print("Running move_test\n")

print("Register a new user")
resp = make_request("register", {"username":"Mover", "password":"123"})

print("Logging in as new user")
resp = make_request("login", {"username":"Mover", "password":"123"})
token = resp["token"]

print("Move rover north")
resp = make_request("move", {"token":token, "direction":"North"})

print("Logout")
resp = make_request("logout", {"token":token})
