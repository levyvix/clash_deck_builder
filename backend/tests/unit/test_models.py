import pytest
from pydantic import ValidationError
from src.models.card import Card
from src.models.deck import Deck

# Sample Card data for testing
sample_card_data = {
    "id": 26000000,
    "name": "Knight",
    "elixir_cost": 3,
    "rarity": "Common",
    "type": "Troop",
    "arena": "Training Camp",
    "image_url": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
    "image_url_evo": None,
}

sample_card_data_evo = {
    "id": 26000001,
    "name": "Knight Evolution",
    "elixir_cost": 3,
    "rarity": "Common",
    "type": "Troop",
    "arena": "Training Camp",
    "image_url": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg.png",
    "image_url_evo": "https://api-assets.clashroyale.com/cards/300/jAj1Q5rclXxU9kVImGqSJxa4wEMfEhvwNQ_4jiGUuqg_evo.png",
}

# --- Card Model Tests ---

def test_card_creation_valid():
    card = Card(**sample_card_data)
    assert card.id == 26000000
    assert card.name == "Knight"
    assert card.elixir_cost == 3
    assert card.rarity == "Common"
    assert card.type == "Troop"
    assert card.image_url is not None

def test_card_creation_with_evolution_image():
    card = Card(**sample_card_data_evo)
    assert card.image_url_evo is not None

def test_card_invalid_id():
    invalid_data = sample_card_data.copy()
    invalid_data["id"] = 0
    with pytest.raises(ValidationError):
        Card(**invalid_data)

def test_card_invalid_name_empty():
    invalid_data = sample_card_data.copy()
    invalid_data["name"] = ""
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Card(**invalid_data)

def test_card_invalid_name_whitespace():
    invalid_data = sample_card_data.copy()
    invalid_data["name"] = "   "
    with pytest.raises(ValidationError, match="Card name cannot be empty"):
        Card(**invalid_data)

def test_card_invalid_elixir_cost_negative():
    invalid_data = sample_card_data.copy()
    invalid_data["elixir_cost"] = -1
    with pytest.raises(ValidationError):
        Card(**invalid_data)

def test_card_invalid_elixir_cost_too_high():
    invalid_data = sample_card_data.copy()
    invalid_data["elixir_cost"] = 11
    with pytest.raises(ValidationError):
        Card(**invalid_data)

def test_card_invalid_rarity():
    invalid_data = sample_card_data.copy()
    invalid_data["rarity"] = "Mythic"
    with pytest.raises(ValidationError, match=r"Rarity must be one of \['Common', 'Rare', 'Epic', 'Legendary', 'Champion'\]"):
        Card(**invalid_data)

def test_card_invalid_type():
    invalid_data = sample_card_data.copy()
    invalid_data["type"] = "Structure"
    with pytest.raises(ValidationError, match=r"Type must be one of \['Troop', 'Spell', 'Building'\]"):
        Card(**invalid_data)

def test_card_invalid_image_url_empty():
    invalid_data = sample_card_data.copy()
    invalid_data["image_url"] = ""
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Card(**invalid_data)

def test_card_invalid_image_url_evo_empty():
    invalid_data = sample_card_data.copy()
    invalid_data["image_url_evo"] = ""
    with pytest.raises(ValidationError, match="Image URL cannot be empty string"):
        Card(**invalid_data)

# --- Deck Model Tests ---

# Create 8 sample cards for a valid deck
cards_for_deck = [Card(**sample_card_data) for _ in range(8)]
cards_for_deck_with_evo = [Card(**sample_card_data) for _ in range(7)]
cards_for_deck_with_evo.append(Card(**sample_card_data_evo))


def test_deck_creation_valid():
    deck = Deck(name="Test Deck", cards=cards_for_deck)
    assert deck.name == "Test Deck"
    assert len(deck.cards) == 8
    assert deck.average_elixir == 3.0 # 8 cards * 3 elixir / 8 cards = 3.0

def test_deck_creation_with_evolution_slots_valid():
    deck = Deck(name="Evo Deck", cards=cards_for_deck_with_evo, evolution_slots=[cards_for_deck_with_evo[-1]])
    assert deck.name == "Evo Deck"
    assert len(deck.cards) == 8
    assert len(deck.evolution_slots) == 1
    # (7 * 3) + (1 * 3) + (1 * 3) / 8 = 21 + 3 + 3 / 8 = 27 / 8 = 3.375 -> 3.38
    assert deck.average_elixir == 3.38

def test_deck_invalid_name_empty():
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Deck(name="", cards=cards_for_deck)

def test_deck_invalid_name_whitespace():
    with pytest.raises(ValidationError, match="Deck name cannot be empty"):
        Deck(name="   ", cards=cards_for_deck)

def test_deck_invalid_cards_count_less_than_8():
    with pytest.raises(ValidationError, match="Deck must have exactly 8 cards"):
        Deck(name="Short Deck", cards=cards_for_deck[:7])

def test_deck_invalid_cards_count_more_than_8():
    with pytest.raises(ValidationError, match="Deck must have exactly 8 cards"):
        Deck(name="Long Deck", cards=cards_for_deck + [Card(**sample_card_data)])

def test_deck_invalid_evolution_slots_more_than_2():
    with pytest.raises(ValidationError, match="Deck cannot have more than 2 evolution slots"):
        Deck(name="Too Many Evo Slots", cards=cards_for_deck_with_evo, evolution_slots=[cards_for_deck_with_evo[-1], cards_for_deck_with_evo[-1], cards_for_deck_with_evo[-1]])

def test_deck_evolution_card_not_in_main_deck():
    card_not_in_deck = Card(id=999, name="NotInDeck", elixir_cost=1, rarity="Common", type="Troop", image_url="url")
    with pytest.raises(ValidationError, match='Evolution slot card "NotInDeck" must also be in the main deck'):
        Deck(name="Invalid Evo Deck", cards=cards_for_deck, evolution_slots=[card_not_in_deck])

def test_deck_average_elixir_calculation():
    card1 = Card(**{**sample_card_data, "elixir_cost": 2})
    card2 = Card(**{**sample_card_data, "elixir_cost": 4})
    cards = [card1] * 4 + [card2] * 4 # 4 cards at 2 elixir, 4 cards at 4 elixir
    deck = Deck(name="Mixed Elixir Deck", cards=cards)
    # (4*2 + 4*4) / 8 = (8 + 16) / 8 = 24 / 8 = 3.0
    assert deck.average_elixir == 3.0

def test_deck_average_elixir_calculation_with_evolution():
    card1 = Card(**{**sample_card_data, "elixir_cost": 2})
    card2 = Card(**{**sample_card_data, "elixir_cost": 4})
    cards = [card1] * 7 + [card2] # 7 cards at 2 elixir, 1 card at 4 elixir
    deck = Deck(name="Mixed Elixir Evo Deck", cards=cards, evolution_slots=[card2])
    # (7*2 + 1*4 + 1*4) / 8 = (14 + 4 + 4) / 8 = 22 / 8 = 2.75
    assert deck.average_elixir == 2.75

def test_deck_average_elixir_calculation_no_cards():
    with pytest.raises(ValidationError, match="Deck must have exactly 8 cards"):
        Deck(name="Empty Deck", cards=[])

def test_deck_update_average_elixir():
    card1 = Card(**{**sample_card_data, "elixir_cost": 1})
    card2 = Card(**{**sample_card_data, "elixir_cost": 5})
    cards = [card1] * 4 + [card2] * 4
    deck = Deck(name="Updatable Deck", cards=cards)
    assert deck.average_elixir == 3.0
    
    # Simulate updating cards
    updated_cards = [Card(**{**sample_card_data, "elixir_cost": 2})] * 8
    deck.cards = updated_cards
    deck.update_average_elixir()
    assert deck.average_elixir == 2.0

def test_deck_auto_calculate_average_elixir_on_init_none():
    card1 = Card(**{**sample_card_data, "elixir_cost": 2})
    cards = [card1] * 8
    deck = Deck(name="Auto Elixir Deck", cards=cards, average_elixir=None)
    assert deck.average_elixir == 2.0

def test_deck_auto_calculate_average_elixir_on_init_not_provided():
    card1 = Card(**{**sample_card_data, "elixir_cost": 2})
    cards = [card1] * 8
    deck = Deck(name="Auto Elixir Deck", cards=cards)
    assert deck.average_elixir == 2.0

def test_deck_auto_calculate_average_elixir_on_init_provided():
    card1 = Card(**{**sample_card_data, "elixir_cost": 2})
    cards = [card1] * 8
    deck = Deck(name="Auto Elixir Deck", cards=cards, average_elixir=5.0)
    assert deck.average_elixir == 5.0 # Should respect provided value if not None

