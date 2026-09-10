from main import app

client = app.test_client()

print("\n🚀 DRUG INTERACTIONS TEST\n")

# ==========================
# LOGIN
# ==========================
login = client.post(
    "/auth/login",
    json={
        "username": "admin",
        "password": "Admin@123456"
    }
)

print("LOGIN:")
print(login.status_code)
print(login.get_json())

if login.status_code != 200:
    print("❌ LOGIN FAILED")
    exit()

token = login.get_json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}"
}


def run_test(title, medicine_ids):
    print(f"\n{title}")

    response = client.post(
        "/drug-interactions/check",
        json={
            "medicine_ids": medicine_ids
        },
        headers=headers
    )

    print("Status:", response.status_code)
    print("Response:")
    print(response.get_json())


# ==========================
# TEST 1
# ==========================
run_test(
    "TEST 1: Warfarin + Ibuprofen",
    [3, 4]
)

# ==========================
# TEST 2
# ==========================
run_test(
    "TEST 2: Warfarin + Omeprazole",
    [3, 8]
)

# ==========================
# TEST 3
# ==========================
run_test(
    "TEST 3: Multiple Medicines",
    [3, 4, 5, 8]
)

# ==========================
# TEST 4
# ==========================
run_test(
    "TEST 4: No Interaction",
    [1, 2]
)

# ==========================
# TEST 5
# ==========================
run_test(
    "TEST 5: One Medicine Only",
    [3]
)

# ==========================
# TEST 6
# ==========================
run_test(
    "TEST 6: Invalid Medicine ID",
    [999]
)

print("\n✅ DRUG INTERACTIONS TEST FINISHED")