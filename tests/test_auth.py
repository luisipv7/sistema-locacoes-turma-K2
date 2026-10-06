import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from database import get_session
from main import app
from models.enums import UserRole
from models.user import User
from security import get_password_hash


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(self.engine)
        with Session(self.engine) as session:
            session.add(User(
                username="test-admin",
                hashed_password=get_password_hash("test-password"),
                role=UserRole.ADMIN,
            ))
            session.commit()

        def test_session():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_session] = test_session
        self.engine_patch = patch("database.engine", self.engine)
        self.engine_patch.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.engine_patch.stop()
        app.dependency_overrides.pop(get_session, None)
        self.engine.dispose()

    def test_login_and_me_with_lowercase_role_and_no_tenant(self):
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(text("SELECT role FROM users")).scalar_one(), "admin")
        response = self.client.post("/auth/login", data={
            "username": "test-admin", "password": "test-password",
        })
        self.assertEqual(response.status_code, 200, response.text)
        token = response.json()["access_token"]
        response = self.client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["role"], "admin")
        self.assertNotIn("hashed_password", response.json())

    def test_invalid_password(self):
        response = self.client.post("/auth/login", data={
            "username": "test-admin", "password": "wrong-password",
        })
        self.assertEqual(response.status_code, 401, response.text)

    def test_inactive_user(self):
        with self.engine.begin() as connection:
            connection.execute(text("UPDATE users SET is_active = 0"))
        response = self.client.post("/auth/login", data={
            "username": "test-admin", "password": "test-password",
        })
        self.assertEqual(response.status_code, 401, response.text)


if __name__ == "__main__":
    unittest.main()
