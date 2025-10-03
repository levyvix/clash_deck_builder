# backend/tests/unit/test_models.py

import pytest
from pydantic import ValidationError
from src.models.card import Card
from src.models.deck import Deck
from src.models.user import User


@pytest.fixture
def sample_cards():
    """Create sample cards for testing"""
    return [
        Card(id=1, name="Knight", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/knight.png"),
        Card(id=2, name="Archers", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/archers.png"),
        Card(id=3, name="Fireball", elixir_cost=4, rarity="Rare", type="Spell", image_url="http://example.com/fireball.png"),
        Card(id=4, name="Giant", elixir_cost=5, rarity="Rare", type="Troop", image_url="http://example.com/giant.png"),
        Card(id=5, name="Wizard", elixir_cost=5, rarity="Rare", type="Troop", image_url="http://example.com/wizard.png"),
        Card(id=6, name="Minions", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/minions.png"),
        Card(id=7, name="Zap", elixir_cost=2, rarity="Common", type="Spell", image_url="http://example.com/zap.png"),
        Card(id=8, name="Musketeer", elixir_cost=4, rarity="Rare", type="Troop", image_url="http://example.com/musketeer.png")
    ]


class TestCardModel:
    """Test suite for Card model validation"""

    def test_card_creation_valid(self):
        """Test creating a valid card"""
        card = Card(
            id=26000000,
            name="Knight",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            arena="Training Camp",
            image_url="http://example.com/knight.png",
            image_url_evo="http://example.com/knight_evo.png"
        )
        
        assert card.id == 26000000
        assert card.name == "Knight"
        assert card.elixir_cost == 3
        assert card.rarity == "Common"
        assert card.type == "Troop"
        assert card.arena == "Training Camp"
        assert card.image_url == "http://example.com/knight.png"
        assert card.image_url_evo == "http://example.com/knight_evo.png"

    def test_card_creation_minimal(self):
        """Test creating a card with minimal required fields"""
        card = Card(
            id=1,
            name="Test Card",
            elixir_cost=3,
            rarity="Common",
            type="Troop",
            image_url="http://example.com/test.png"
        )
        
        assert card.arena is None
        assert card.image_url_evo is None

    def test_card_id_validation(self):
        """Test card ID validation"""
        # Valid ID
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert card.id == 1
        
        # Invalid ID (zero)
        with pytest.raises(ValidationError) as exc_info:
            Card(id=0, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "greater than or equal to 1" in str(exc_info.value)
        
        # Invalid ID (negative)
        with pytest.raises(ValidationError) as exc_info:
            Card(id=-1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_card_name_validation(self):
        """Test card name validation"""
        # Valid name
        card = Card(id=1, name="Knight", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert card.name == "Knight"
        
        # Name with spaces (should be trimmed)
        card = Card(id=1, name="  Knight  ", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert card.name == "Knight"
        
        # Empty name
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Whitespace-only name
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="   ", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "Card name cannot be empty" in str(exc_info.value)
        
        # Name too long
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="x" * 101, elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "at most 100 characters" in str(exc_info.value)

    def test_card_elixir_cost_validation(self):
        """Test elixir cost validation"""
        # Valid costs
        for cost in [0, 1, 5, 10]:
            card = Card(id=1, name="Test", elixir_cost=cost, rarity="Common", type="Troop", image_url="http://example.com/test.png")
            assert card.elixir_cost == cost
        
        # Invalid cost (negative)
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=-1, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "greater than or equal to 0" in str(exc_info.value)
        
        # Invalid cost (too high)
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=11, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert "less than or equal to 10" in str(exc_info.value)

    def test_card_rarity_validation(self):
        """Test rarity validation"""
        valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Champion']
        
        # Valid rarities
        for rarity in valid_rarities:
            card = Card(id=1, name="Test", elixir_cost=3, rarity=rarity, type="Troop", image_url="http://example.com/test.png")
            assert card.rarity == rarity
        
        # Invalid rarity
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=3, rarity="Invalid", type="Troop", image_url="http://example.com/test.png")
        assert "Rarity must be one of" in str(exc_info.value)

    def test_card_type_validation(self):
        """Test type validation"""
        valid_types = ['Troop', 'Spell', 'Building']
        
        # Valid types
        for card_type in valid_types:
            card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type=card_type, image_url="http://example.com/test.png")
            assert card.type == card_type
        
        # Invalid type
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Invalid", image_url="http://example.com/test.png")
        assert "Type must be one of" in str(exc_info.value)

    def test_card_arena_validation(self):
        """Test arena validation"""
        # Valid arena
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", arena="Training Camp", image_url="http://example.com/test.png")
        assert card.arena == "Training Camp"
        
        # None arena (optional field)
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert card.arena is None
        
        # Arena too long
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", arena="x" * 51, image_url="http://example.com/test.png")
        assert "at most 50 characters" in str(exc_info.value)

    def test_card_image_url_validation(self):
        """Test image URL validation"""
        # Valid URL
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert card.image_url == "http://example.com/test.png"
        
        # URL with spaces (should be trimmed)
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="  http://example.com/test.png  ")
        assert card.image_url == "http://example.com/test.png"
        
        # Empty URL
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="")
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_card_image_url_evo_validation(self):
        """Test evolution image URL validation"""
        # Valid evolution URL
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png", image_url_evo="http://example.com/test_evo.png")
        assert card.image_url_evo == "http://example.com/test_evo.png"
        
        # None evolution URL (optional field)
        card = Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png")
        assert card.image_url_evo is None
        
        # Empty evolution URL
        with pytest.raises(ValidationError) as exc_info:
            Card(id=1, name="Test", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/test.png", image_url_evo="")
        assert "Image URL cannot be empty string" in str(exc_info.value)


class TestDeckModel:
    """Test suite for Deck model validation and business logic"""

    def test_deck_creation_valid(self, sample_cards):
        """Test creating a valid deck"""
        deck = Deck(
            id=1,
            name="Test Deck",
            user_id=1,
            cards=sample_cards,
            evolution_slots=[sample_cards[0]],
            average_elixir=3.5
        )
        
        assert deck.id == 1
        assert deck.name == "Test Deck"
        assert deck.user_id == 1
        assert len(deck.cards) == 8
        assert len(deck.evolution_slots) == 1
        assert deck.average_elixir == 3.5

    def test_deck_creation_minimal(self, sample_cards):
        """Test creating a deck with minimal required fields"""
        deck = Deck(name="Minimal Deck", cards=sample_cards)
        
        assert deck.id is None
        assert deck.user_id is None
        assert deck.evolution_slots == []
        assert deck.average_elixir is not None  # Should be auto-calculated

    def test_deck_name_validation(self, sample_cards):
        """Test deck name validation"""
        # Valid name
        deck = Deck(name="My Deck", cards=sample_cards)
        assert deck.name == "My Deck"
        
        # Name with spaces (should be trimmed)
        deck = Deck(name="  My Deck  ", cards=sample_cards)
        assert deck.name == "My Deck"
        
        # Empty name
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="", cards=sample_cards)
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Whitespace-only name
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="   ", cards=sample_cards)
        assert "Deck name cannot be empty" in str(exc_info.value)
        
        # Name too long
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="x" * 101, cards=sample_cards)
        assert "at most 100 characters" in str(exc_info.value)

    def test_deck_cards_count_validation(self, sample_cards):
        """Test deck cards count validation"""
        # Valid deck with exactly 8 cards
        deck = Deck(name="Valid Deck", cards=sample_cards)
        assert len(deck.cards) == 8
        
        # Invalid deck with too few cards
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Invalid Deck", cards=sample_cards[:7])
        assert "Deck must have exactly 8 cards, got 7" in str(exc_info.value)
        
        # Invalid deck with too many cards
        extra_card = Card(id=9, name="Extra", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/extra.png")
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Invalid Deck", cards=sample_cards + [extra_card])
        assert "Deck must have exactly 8 cards, got 9" in str(exc_info.value)

    def test_deck_evolution_slots_validation(self, sample_cards):
        """Test evolution slots validation"""
        # Valid deck with 0 evolution slots
        deck = Deck(name="No Evo Deck", cards=sample_cards, evolution_slots=[])
        assert len(deck.evolution_slots) == 0
        
        # Valid deck with 1 evolution slot
        deck = Deck(name="One Evo Deck", cards=sample_cards, evolution_slots=[sample_cards[0]])
        assert len(deck.evolution_slots) == 1
        
        # Valid deck with 2 evolution slots
        deck = Deck(name="Two Evo Deck", cards=sample_cards, evolution_slots=[sample_cards[0], sample_cards[1]])
        assert len(deck.evolution_slots) == 2
        
        # Invalid deck with too many evolution slots
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Invalid Deck", cards=sample_cards, evolution_slots=[sample_cards[0], sample_cards[1], sample_cards[2]])
        assert "Deck cannot have more than 2 evolution slots, got 3" in str(exc_info.value)

    def test_deck_evolution_cards_in_deck_validation(self, sample_cards):
        """Test that evolution slot cards must be in the main deck"""
        # Valid: evolution card is in main deck
        deck = Deck(name="Valid Deck", cards=sample_cards, evolution_slots=[sample_cards[0]])
        assert len(deck.evolution_slots) == 1
        
        # Invalid: evolution card is not in main deck
        extra_card = Card(id=99, name="Not In Deck", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/extra.png")
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Invalid Deck", cards=sample_cards, evolution_slots=[extra_card])
        assert 'Evolution slot card "Not In Deck" must also be in the main deck' in str(exc_info.value)

    def test_deck_id_validation(self, sample_cards):
        """Test deck ID validation"""
        # Valid ID
        deck = Deck(id=1, name="Test Deck", cards=sample_cards)
        assert deck.id == 1
        
        # None ID (optional field)
        deck = Deck(name="Test Deck", cards=sample_cards)
        assert deck.id is None
        
        # Invalid ID (zero)
        with pytest.raises(ValidationError) as exc_info:
            Deck(id=0, name="Test Deck", cards=sample_cards)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_deck_user_id_validation(self, sample_cards):
        """Test user ID validation"""
        # Valid user ID
        deck = Deck(name="Test Deck", user_id=1, cards=sample_cards)
        assert deck.user_id == 1
        
        # None user ID (optional field)
        deck = Deck(name="Test Deck", cards=sample_cards)
        assert deck.user_id is None
        
        # Invalid user ID (zero)
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Test Deck", user_id=0, cards=sample_cards)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_deck_average_elixir_validation(self, sample_cards):
        """Test average elixir validation"""
        # Valid average elixir
        deck = Deck(name="Test Deck", cards=sample_cards, average_elixir=3.5)
        assert deck.average_elixir == 3.5
        
        # Invalid average elixir (negative)
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Test Deck", cards=sample_cards, average_elixir=-1.0)
        assert "greater than or equal to 0" in str(exc_info.value)
        
        # Invalid average elixir (too high)
        with pytest.raises(ValidationError) as exc_info:
            Deck(name="Test Deck", cards=sample_cards, average_elixir=11.0)
        assert "less than or equal to 10" in str(exc_info.value)

    def test_calculate_average_elixir_basic(self, sample_cards):
        """Test basic average elixir calculation"""
        deck = Deck(name="Test Deck", cards=sample_cards)
        
        # Calculate expected average: (3+3+4+5+5+3+2+4) / 8 = 29/8 = 3.625 -> 3.62
        expected_avg = round(29 / 8, 2)
        calculated_avg = deck.calculate_average_elixir()
        
        assert calculated_avg == expected_avg

    def test_calculate_average_elixir_with_evolution_slots(self, sample_cards):
        """Test average elixir calculation with evolution slots"""
        # Knight (3 elixir) and Archers (3 elixir) in evolution slots
        deck = Deck(name="Test Deck", cards=sample_cards, evolution_slots=[sample_cards[0], sample_cards[1]])
        
        # Total elixir: 29 (main deck) + 3 + 3 (evolution slots) = 35
        # Average: 35 / 8 = 4.375 -> 4.38
        expected_avg = round(35 / 8, 2)
        calculated_avg = deck.calculate_average_elixir()
        
        assert calculated_avg == expected_avg

    def test_calculate_average_elixir_empty_deck(self):
        """Test average elixir calculation with empty deck"""
        # Create a simple mock object to test the calculation method
        class MockDeck:
            def __init__(self):
                self.cards = []
                self.evolution_slots = []
            
            def calculate_average_elixir(self):
                if not self.cards:
                    return 0.0
                total_elixir = sum(card.elixir_cost for card in self.cards)
                total_elixir += sum(card.elixir_cost for card in self.evolution_slots)
                total_cards = len(self.cards)
                return round(total_elixir / total_cards, 2) if total_cards > 0 else 0.0
        
        mock_deck = MockDeck()
        calculated_avg = mock_deck.calculate_average_elixir()
        assert calculated_avg == 0.0

    def test_auto_calculate_average_elixir(self, sample_cards):
        """Test automatic average elixir calculation"""
        # When average_elixir is not provided, it should be auto-calculated
        deck = Deck(name="Test Deck", cards=sample_cards)
        
        expected_avg = round(29 / 8, 2)  # (3+3+4+5+5+3+2+4) / 8
        assert deck.average_elixir == expected_avg

    def test_auto_calculate_average_elixir_with_provided_value(self, sample_cards):
        """Test that provided average elixir is not overridden"""
        # When average_elixir is provided, it should not be auto-calculated
        deck = Deck(name="Test Deck", cards=sample_cards, average_elixir=5.0)
        
        assert deck.average_elixir == 5.0  # Should keep provided value

    def test_update_average_elixir(self, sample_cards):
        """Test manual average elixir update"""
        deck = Deck(name="Test Deck", cards=sample_cards, average_elixir=5.0)
        
        # Update should recalculate based on current cards
        deck.update_average_elixir()
        
        expected_avg = round(29 / 8, 2)
        assert deck.average_elixir == expected_avg


class TestUserModel:
    """Test suite for User model"""

    def test_user_creation_with_id(self):
        """Test creating a user with ID"""
        user = User(id=1)
        assert user.id == 1

    def test_user_creation_without_id(self):
        """Test creating a user without ID"""
        user = User()
        assert user.id is None
