
from modules.auth import authenticate_user
import getpass

print("\n========== PNEUMOCARE LOGIN TEST ==========\n")

username = input("Username: ")
password = getpass.getpass("Password: ")

result = authenticate_user(
    username,
    password,
    "admin"
)

print("\nResult:", result["message"])

if result["success"]:
    print("Account ID:", result["account_id"])
    print("Username:", result["username"])
    print("Role:", result["role"])
