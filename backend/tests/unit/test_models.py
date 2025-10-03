# backend/tests/unit/test_models.py

import pytest
from src.models.card import Card
from src.models.deck import Deck
from src.models.user import User

def test_card_model():
    card = Card(id=1, name="Archer", elixir_cost=3, rarity="Common", type="Troop", image_url="http://example.com/archer.png")
    assert card.name == "Archer"

def test_deck_model():
    # Create 8 cards as required by the deck validation
    cards = []
    for i in range(8):
        card = Card(
            id=i+1, 
            name=f"Card{i+1}", 
            elixir_cost=3, 
            rarity="Common", 
            type="Troop", 
            image_url=f"http://example.com/card{i+1}.png"
        )
        cards.append(card)
    
    deck = Deck(name="Test Deck", cards=cards, evolution_slots=[], average_elixir=3.0)
    assert len(deck.cards) == 8
    assert deck.name == "Test Deck"
    assert deck.average_elixir == 3.0

def test_user_model():
    user = User(id=1)
    assert user.id == 1
