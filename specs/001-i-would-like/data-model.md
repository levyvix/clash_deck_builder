# Data Model: Clash Royale Deck Builder

## Entities

### Card
- Name: String
- Elixir Cost: Integer
- Rarity: String (e.g., Common, Rare, Epic, Legendary, Champion, Tower)
- Type: String (e.g., Troop, Spell, Building, Evolution)
- Arena: String/Integer (depending on API data)
- Image: URL (normal, evolved)

### Deck
- Name: String
- Cards: List of Card IDs (up to 8)
- Evolution Slots: List of Card IDs (up to 2, subset of Cards)
- Average Elixir Cost: Float
- User ID: Foreign Key to User (if multi-user)

### User
- ID: Primary Key
- Saved Decks: List of Deck IDs (up to 20)
