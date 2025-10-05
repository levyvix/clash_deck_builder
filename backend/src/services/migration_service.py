# backend/src/services/migration_service.py

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.user import User
from ..models.deck import Deck
from ..services.deck_service import DeckService
from ..utils.database import get_db_session
from ..exceptions import DatabaseError, DeckValidationError

logger = logging.getLogger(__name__)


class MigrationService:
    """Service for handling user data migration and onboarding."""

    def __init__(self):
        pass

    def handle_user_onboarding(self, user: User, migration_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle first-time user onboarding and data migration.

        Args:
            user: Newly created or existing user
            migration_data: Optional data to migrate from anonymous usage

        Returns:
            Dict containing onboarding status and migration results
        """
        try:
            logger.info(f"Starting onboarding process for user: {user.email}")

            onboarding_result = {
                "is_new_user": self._is_new_user(user),
                "needs_profile_setup": self._needs_profile_setup(user),
                "migration_performed": False,
                "migrated_decks_count": 0,
                "onboarding_steps": self._get_onboarding_steps(user),
            }

            # Handle migration if data is provided
            if migration_data and migration_data.get("decks"):
                migration_result = self._migrate_anonymous_decks(user, migration_data["decks"])
                onboarding_result.update(
                    {
                        "migration_performed": True,
                        "migrated_decks_count": migration_result["migrated_count"],
                        "migration_errors": migration_result.get("errors", []),
                    }
                )

            logger.info(f"Onboarding completed for user {user.email}: {onboarding_result}")
            return onboarding_result

        except Exception as e:
            logger.error(f"Onboarding failed for user {user.email}: {e}")
            raise DatabaseError(f"Onboarding process failed: {e}")

    def _is_new_user(self, user: User) -> bool:
        """Check if this is a new user (created within last 5 minutes)."""
        if not user.created_at:
            return True

        time_diff = datetime.now() - user.created_at
        return time_diff.total_seconds() < 300  # 5 minutes

    def _needs_profile_setup(self, user: User) -> bool:
        """Check if user needs to complete profile setup."""
        # User needs profile setup if they don't have an avatar
        return not user.avatar

    def _get_onboarding_steps(self, user: User) -> List[Dict[str, Any]]:
        """Get list of onboarding steps for the user."""
        steps = []

        # Step 1: Welcome message (always shown for new users)
        if self._is_new_user(user):
            steps.append(
                {
                    "id": "welcome",
                    "title": "Welcome to Clash Royale Deck Builder!",
                    "description": "Your Google account has been successfully connected.",
                    "completed": True,
                    "required": False,
                }
            )

        # Step 2: Avatar selection (if no avatar set)
        if not user.avatar:
            steps.append(
                {
                    "id": "avatar_selection",
                    "title": "Choose Your Avatar",
                    "description": "Select a Clash Royale card as your profile avatar.",
                    "completed": False,
                    "required": False,
                    "action": "select_avatar",
                }
            )

        # Step 3: Profile customization
        steps.append(
            {
                "id": "profile_setup",
                "title": "Customize Your Profile",
                "description": "Update your display name and complete your profile.",
                "completed": bool(user.name and user.name != user.email.split("@")[0]),
                "required": False,
                "action": "edit_profile",
            }
        )

        # Step 4: Start building decks
        steps.append(
            {
                "id": "start_building",
                "title": "Start Building Decks",
                "description": "Create your first deck and save it to your account.",
                "completed": False,
                "required": False,
                "action": "build_deck",
            }
        )

        return steps

    def _migrate_anonymous_decks(self, user: User, anonymous_decks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Migrate anonymous deck data to authenticated user account.

        Args:
            user: Target user for migration
            anonymous_decks: List of deck data from anonymous usage

        Returns:
            Dict containing migration results
        """
        try:
            logger.info(f"Migrating {len(anonymous_decks)} anonymous decks for user {user.email}")

            migrated_count = 0
            errors = []

            for i, deck_data in enumerate(anonymous_decks):
                try:
                    # Validate and create deck
                    deck = self._create_deck_from_anonymous_data(deck_data, user)

                    if deck:
                        migrated_count += 1
                        logger.debug(f"Migrated deck: {deck.name}")

                except Exception as e:
                    error_msg = f"Failed to migrate deck {i + 1}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)

            result = {"migrated_count": migrated_count, "total_decks": len(anonymous_decks), "errors": errors}

            logger.info(f"Migration completed for user {user.email}: {result}")
            return result

        except Exception as e:
            logger.error(f"Migration failed for user {user.email}: {e}")
            raise DatabaseError(f"Deck migration failed: {e}")

    def _create_deck_from_anonymous_data(self, deck_data: Dict[str, Any], user: User) -> Optional[Deck]:
        """
        Create a deck from anonymous data format.

        Args:
            deck_data: Anonymous deck data
            user: Target user

        Returns:
            Created Deck or None if creation failed
        """
        try:
            # Extract deck information from anonymous format
            # This assumes anonymous decks were stored in a similar format
            deck_name = deck_data.get("name", "Imported Deck")
            cards = deck_data.get("cards", [])
            evolution_slots = deck_data.get("evolution_slots", [])

            # Validate deck has required cards
            if not cards or len(cards) != 8:
                logger.warning(f"Invalid deck data - expected 8 cards, got {len(cards)}")
                return None

            # Create deck object
            deck = Deck(name=deck_name, cards=cards, evolution_slots=evolution_slots, user_id=user.id)

            # Use deck service to create and validate
            with get_db_session() as db_session:
                deck_service = DeckService(db_session)
                created_deck = deck_service.create_deck(deck, user)
                return created_deck

        except (DeckValidationError, DatabaseError) as e:
            logger.warning(f"Failed to create deck from anonymous data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating deck from anonymous data: {e}")
            return None

    def get_onboarding_status(self, user: User) -> Dict[str, Any]:
        """
        Get current onboarding status for a user.

        Args:
            user: User to check onboarding status for

        Returns:
            Dict containing current onboarding status
        """
        try:
            return {
                "is_new_user": self._is_new_user(user),
                "needs_profile_setup": self._needs_profile_setup(user),
                "onboarding_steps": self._get_onboarding_steps(user),
                "profile_completion": self._calculate_profile_completion(user),
            }

        except Exception as e:
            logger.error(f"Failed to get onboarding status for user {user.email}: {e}")
            raise DatabaseError(f"Failed to get onboarding status: {e}")

    def _calculate_profile_completion(self, user: User) -> Dict[str, Any]:
        """Calculate profile completion percentage and missing items."""
        completion_items = {
            "has_avatar": bool(user.avatar),
            "has_custom_name": bool(user.name and user.name != user.email.split("@")[0]),
            "has_email": bool(user.email),  # Always true for Google OAuth users
        }

        completed_count = sum(1 for completed in completion_items.values() if completed)
        total_count = len(completion_items)
        percentage = int((completed_count / total_count) * 100)

        return {
            "percentage": percentage,
            "completed_items": completed_count,
            "total_items": total_count,
            "items": completion_items,
            "is_complete": percentage == 100,
        }

    def mark_onboarding_step_completed(self, user: User, step_id: str) -> bool:
        """
        Mark an onboarding step as completed.

        Args:
            user: User completing the step
            step_id: ID of the step being completed

        Returns:
            True if step was marked as completed
        """
        try:
            logger.info(f"Marking onboarding step '{step_id}' as completed for user {user.email}")

            # For now, we don't persist onboarding step completion in the database
            # Steps are calculated dynamically based on user profile state
            # This method exists for future extensibility

            return True

        except Exception as e:
            logger.error(f"Failed to mark onboarding step completed for user {user.email}: {e}")
            return False
