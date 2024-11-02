from app.utils import create_auth_token


async def test_login(mocker, client, test_user):
    # Test for error response with invalid credentials
    response = await client.post(
        "/auth/login",
        json={"email": "invalid@email.com", "password": "invalidpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "status": "failure",
        "message": "Invalid credentials",
    }

    # Test for success response valid credentials
    response = await client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Login successful",
        "data": {"token": mocker.ANY},
    }


async def test_retrieve_all_articles(client, test_article):
    # Verify that all articles are retrieved successfully
    response = await client.get("/articles")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["message"] == "Articles fetched successfully"
    data = result["data"]
    assert len(data) > 0
    assert any(isinstance(obj["title"], str) for obj in data)


async def test_retrieve_article_detail(client, test_article):
    # Verify that a single article detail was received successfully
    response = await client.get(f"/articles/{test_article.slug}")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Article details fetched successfully",
        "data": {
            "title": test_article.title,
            "slug": test_article.slug,
            "desc": test_article.desc,
            "likes_count": test_article.likes_count,
            "created_at": test_article.created_at.isoformat(),
            "updated_at": test_article.updated_at.isoformat(),
        },
    }

    # Verify that an error returns for invalid slug
    response = await client.get("/articles/invalid_slug")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Article does not exist!",
    }


async def test_like_article(client, test_article, test_user):
    # Verify that an error returns for unauthorized user
    response = await client.get(f"/articles/{test_article.slug}/like")
    assert response.status_code == 401
    assert response.json() == {
        "status": "failure",
        "message": "Unauthorized User!",
    }

    # Set authorization for client
    token = create_auth_token(test_user.id)
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    # Verify that an error returns for invalid slug
    response = await client.get("/articles/invalid_slug/like")
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "message": "Article does not exist!",
    }

    # Verify that the article was liked or unliked successfully
    response = await client.get(f"/articles/{test_article.slug}/like")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Like added successfully",
    }
