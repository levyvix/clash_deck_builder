# backend/tests/unit/test_models.py

import pytest
from backend.src.models.card import Card
from backend.src.models.deck import Deck
from backend.src.models.user import User

def test_card_model():
    card = Card(id=1, name="Archer", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/archer.png")
    assert card.name == "Archer"

def test_deck_model():
    card1 = Card(id=1, name="Archer", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/archer.png")
    card2 = Card(id=2, name="Giant", elixir_cost=5, rarity="Rare", type="Troop", image_url="http://example.com/giant.png")
    deck = Deck(name="Test Deck", cards=[card1, card2], evolution_slots=[], average_elixir=4.0)
    assert len(deck.cards) == 2

def test_user_model():
    user = User(id=1)
    assert user.id == 1
