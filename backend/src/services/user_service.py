# backend/src/services/user_service.py

import logging
from typing import Optional, List
from datetime import datetime, timezone
from mysql.connector import Error as MySQLError

from ..models.user import User, UserCreate, UserUpdate
from ..utils.database import get_db_session
from ..exceptions.auth_exceptions import UserNotFoundError
from ..utils.database import DatabaseError

logger = logging.getLogger(__name__)


class UserService:
    """Service for user database operations."""

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user in the database."""
        try:
            user_id = user_data.generate_id()
            now = datetime.now(timezone.utc)

            with get_db_session() as session:
                query = """
                    INSERT INTO users (id, google_id, email, name, avatar, created_at, updated_at)
                    VALUES (%(id)s, %(google_id)s, %(email)s, %(name)s, %(avatar)s, %(created_at)s, %(updated_at)s)
                """

                params = {
                    "id": user_id,
                    "google_id": user_data.google_id,
                    "email": user_data.email,
                    "name": user_data.name,
                    "avatar": user_data.avatar,
                    "created_at": now,
                    "updated_at": now,
                }

                session.execute(query, params)

                fetch_query = """
                    SELECT id, google_id, email, name, avatar, created_at, updated_at
                    FROM users
                    WHERE id = %(user_id)s
                """

                session.execute(fetch_query, {"user_id": user_id})
                result = session.fetchone()

                if not result:
                    raise DatabaseError("Failed to retrieve created user")

                created_user = User(**result)
                logger.info(f"Created new user: {created_user.email} (ID: {user_id})")
                return created_user

        except MySQLError as e:
            if e.errno == 1062:
                logger.warning(f"Attempted to create duplicate user with Google ID: {user_data.google_id}")
                raise DatabaseError("User with this Google ID already exists")
            logger.error(f"MySQL error creating user: {e}")
            raise DatabaseError(f"Failed to create user: {e}")
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            raise DatabaseError(f"Failed to create user: {e}")

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        try:
            with get_db_session() as session:
                query = """
                    SELECT id, google_id, email, name, avatar, created_at, updated_at
                    FROM users
                    WHERE id = %(user_id)s
                """

                session.execute(query, {"user_id": user_id})
                result = session.fetchone()

                if result:
                    return User(**result)
                return None

        except MySQLError as e:
            logger.error(f"MySQL error getting user by ID {user_id}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by ID {user_id}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")

    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """
        Get user by Google ID.

        Args:
            google_id: Google user ID

        Returns:
            User object if found, None otherwise
        """
        try:
            with get_db_session() as session:
                query = """
                    SELECT id, google_id, email, name, avatar, created_at, updated_at
                    FROM users
                    WHERE google_id = %(google_id)s
                """

                session.execute(query, {"google_id": google_id})
                result = session.fetchone()

                if result:
                    return User(**result)
                return None

        except MySQLError as e:
            logger.error(f"MySQL error getting user by Google ID {google_id}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by Google ID {google_id}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        try:
            with get_db_session() as session:
                query = """
                    SELECT id, google_id, email, name, avatar, created_at, updated_at
                    FROM users
                    WHERE email = %(email)s
                """

                session.execute(query, {"email": email})
                result = session.fetchone()

                if result:
                    return User(**result)
                return None

        except MySQLError as e:
            logger.error(f"MySQL error getting user by email {email}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by email {email}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")

    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            user_id: User ID
            user_data: UserUpdate object with updated information

        Returns:
            Updated User object

        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If update fails
        """
        try:
            # Check if user exists
            existing_user = self.get_user_by_id(user_id)
            if not existing_user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            # Build update query dynamically based on provided fields
            update_fields = []
            params = {"user_id": user_id, "updated_at": datetime.now(timezone.utc)}

            if user_data.name is not None:
                update_fields.append("name = %(name)s")
                params["name"] = user_data.name

            if user_data.avatar is not None:
                update_fields.append("avatar = %(avatar)s")
                params["avatar"] = user_data.avatar

            if not update_fields:
                # No fields to update, return existing user
                return existing_user

            update_fields.append("updated_at = %(updated_at)s")

            with get_db_session() as session:
                query = f"""
                    UPDATE users
                    SET {', '.join(update_fields)}
                    WHERE id = %(user_id)s
                """

                session.execute(query, params)

                if session.rowcount == 0:
                    raise UserNotFoundError(f"User with ID {user_id} not found")

                # Fetch updated user
                updated_user = self.get_user_by_id(user_id)
                if not updated_user:
                    raise DatabaseError("Failed to retrieve updated user")

                logger.info(f"Updated user: {updated_user.email} (ID: {user_id})")
                return updated_user

        except (UserNotFoundError, DatabaseError):
            raise
        except MySQLError as e:
            logger.error(f"MySQL error updating user {user_id}: {e}")
            raise DatabaseError(f"Failed to update user: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating user {user_id}: {e}")
            raise DatabaseError(f"Failed to update user: {e}")

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user from database.

        Args:
            user_id: User ID

        Returns:
            True if user was deleted, False if user didn't exist

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            with get_db_session() as session:
                query = "DELETE FROM users WHERE id = %(user_id)s"
                session.execute(query, {"user_id": user_id})

                deleted = session.rowcount > 0
                if deleted:
                    logger.info(f"Deleted user with ID: {user_id}")
                else:
                    logger.warning(f"Attempted to delete non-existent user: {user_id}")

                return deleted

        except MySQLError as e:
            logger.error(f"MySQL error deleting user {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting user {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user: {e}")

    def get_or_create_user(self, google_user_info: dict) -> User:
        """
        Get existing user by Google ID or create new user.

        Args:
            google_user_info: Dict containing Google user information

        Returns:
            User object (existing or newly created)

        Raises:
            DatabaseError: If user creation/retrieval fails
        """
        try:
            google_id = google_user_info["google_id"]

            # Try to get existing user
            existing_user = self.get_user_by_google_id(google_id)
            if existing_user:
                logger.info(f"Found existing user for Google ID: {google_id}")
                return existing_user

            # Create new user
            user_create = UserCreate(
                google_id=google_id,
                email=google_user_info["email"],
                name=google_user_info.get("name", google_user_info["email"].split("@")[0]),
                avatar=None,  # Will be set later by user
            )

            new_user = self.create_user(user_create)
            logger.info(f"Created new user for Google ID: {google_id}")
            return new_user

        except Exception as e:
            logger.error(f"Failed to get or create user for Google ID {google_id}: {e}")
            raise DatabaseError(f"Failed to get or create user: {e}")

    def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        List users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of User objects
        """
        try:
            with get_db_session() as session:
                query = """
                    SELECT id, google_id, email, name, avatar, created_at, updated_at
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                """

                session.execute(query, {"limit": limit, "offset": offset})
                results = session.fetchall()

                return [User(**result) for result in results]

        except MySQLError as e:
            logger.error(f"MySQL error listing users: {e}")
            raise DatabaseError(f"Failed to list users: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing users: {e}")
            raise DatabaseError(f"Failed to list users: {e}")

    def count_users(self) -> int:
        """
        Get total number of users.

        Returns:
            Total user count
        """
        try:
            with get_db_session() as session:
                query = "SELECT COUNT(*) as count FROM users"
                session.execute(query)
                result = session.fetchone()

                return result["count"] if result else 0

        except MySQLError as e:
            logger.error(f"MySQL error counting users: {e}")
            raise DatabaseError(f"Failed to count users: {e}")
        except Exception as e:
            logger.error(f"Unexpected error counting users: {e}")
            raise DatabaseError(f"Failed to count users: {e}")

    def create_or_update_user(self, google_id: str, email: str, name: str) -> User:
        """
        Create a new user or update existing user from Google OAuth data.

        Args:
            google_id: Google user ID
            email: User email address
            name: User display name

        Returns:
            User object (existing or newly created)

        Raises:
            DatabaseError: If user creation/update fails
        """
        try:
            # Try to get existing user by Google ID
            existing_user = self.get_user_by_google_id(google_id)

            if existing_user:
                # Update existing user with latest info from Google
                user_update = UserUpdate(name=name)
                updated_user = self.update_user(existing_user.id, user_update)
                logger.info(f"Updated existing user: {updated_user.email} (ID: {existing_user.id})")
                return updated_user
            else:
                # Create new user
                user_create = UserCreate(
                    google_id=google_id, email=email, name=name, avatar=None  # Will be set later by user
                )
                new_user = self.create_user(user_create)
                logger.info(f"Created new user: {new_user.email} (ID: {new_user.id})")
                return new_user

        except Exception as e:
            logger.error(f"Failed to create or update user for Google ID {google_id}: {e}")
            raise DatabaseError(f"Failed to create or update user: {e}")
