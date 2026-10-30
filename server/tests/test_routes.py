def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {"message": "Welcome to the Recipe Planner API!"}


def test_signup(client):
    response = client.post('/signup', json={
        "username": "chef_test",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "chef_test"
    assert "id" in data


def test_login_and_check_session(client):
    # First sign up a user
    client.post('/signup', json={
        "username": "chef_test",
        "password": "password123"
    })

    # Test login
    response = client.post('/login', json={
        "username": "chef_test",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.get_json()["username"] == "chef_test"

    # Test check session
    session_response = client.get('/check_session')
    assert session_response.status_code == 200
    assert session_response.get_json()["username"] == "chef_test"


def test_logout(client):
    # Signup & Login
    client.post('/signup', json={
        "username": "chef_test",
        "password": "password123"
    })
    client.post('/login', json={
        "username": "chef_test",
        "password": "password123"
    })

    # Test logout
    response = client.delete('/logout')
    assert response.status_code == 204

    # Verify session is cleared
    check = client.get('/check_session')
    assert check.status_code == 401


def test_recipe_crud(client):
    # 1. Attempt to access recipes unauthorized
    res = client.get('/recipes')
    assert res.status_code == 401

    # 2. Signup and log in
    client.post('/signup', json={
        "username": "chef_test",
        "password": "password123"
    })
    client.post('/login', json={
        "username": "chef_test",
        "password": "password123"
    })

    # 3. POST /recipes (Create)
    create_res = client.post('/recipes', json={
        "title": "Pancakes",
        "instructions": "Mix flour, milk, and eggs. Cook on skillet.",
        "prep_time_minutes": 15,
        "ingredients": "Flour, Milk, Eggs",
        "is_favorite": True
    })
    assert create_res.status_code == 201
    recipe_data = create_res.get_json()
    recipe_id = recipe_data["id"]
    assert recipe_data["title"] == "Pancakes"

    # 4. GET /recipes (Read All with Pagination)
    get_all_res = client.get('/recipes')
    assert get_all_res.status_code == 200
    assert len(get_all_res.get_json()["recipes"]) == 1

    # 5. GET /recipes/<id> (Read One)
    get_one_res = client.get(f'/recipes/{recipe_id}')
    assert get_one_res.status_code == 200
    assert get_one_res.get_json()["title"] == "Pancakes"

    # 6. PATCH /recipes/<id> (Update)
    patch_res = client.patch(f'/recipes/{recipe_id}', json={
        "title": "Fluffy Pancakes"
    })
    assert patch_res.status_code == 200
    assert patch_res.get_json()["title"] == "Fluffy Pancakes"

    # 7. DELETE /recipes/<id> (Delete)
    delete_res = client.delete(f'/recipes/{recipe_id}')
    assert delete_res.status_code == 204

    # Verify it's gone
    verify_delete = client.get(f'/recipes/{recipe_id}')
    assert verify_delete.status_code == 404