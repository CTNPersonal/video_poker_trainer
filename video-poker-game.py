import streamlit as st
import random
from itertools import combinations

# Define card ranks and suits
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']

# Define hand rankings
HAND_RANKINGS = {
    "Royal Flush": 800,
    "Straight Flush": 50,
    "Four of a Kind": 25,
    "Full House": 9,
    "Flush": 6,
    "Straight": 4,
    "Three of a Kind": 3,
    "Two Pair": 2,
    "Jacks or Better": 1,
    "Nothing": 0
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in RANKS for suit in SUITS]
        random.shuffle(self.cards)
    
    def draw(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
    
    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

def evaluate_hand(hand):
    ranks = [card.rank for card in hand.cards]
    suits = [card.suit for card in hand.cards]
    
    # Check for flush
    is_flush = len(set(suits)) == 1
    
    # Check for straight
    rank_values = [RANKS.index(rank) for rank in ranks]
    rank_values.sort()
    is_straight = (max(rank_values) - min(rank_values) == 4) and len(set(rank_values)) == 5
    
    # Count occurrences of each rank
    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
    
    if is_flush and is_straight and set(ranks) == set(['10', 'J', 'Q', 'K', 'A']):
        return "Royal Flush"
    elif is_flush and is_straight:
        return "Straight Flush"
    elif 4 in rank_counts.values():
        return "Four of a Kind"
    elif set(rank_counts.values()) == {2, 3}:
        return "Full House"
    elif is_flush:
        return "Flush"
    elif is_straight:
        return "Straight"
    elif 3 in rank_counts.values():
        return "Three of a Kind"
    elif list(rank_counts.values()).count(2) == 2:
        return "Two Pair"
    elif 2 in rank_counts.values() and any(rank in ['J', 'Q', 'K', 'A'] for rank in rank_counts if rank_counts[rank] == 2):
        return "Jacks or Better"
    else:
        return "Nothing"

def get_optimal_move(hand):
    best_hold = []
    best_ev = -1
    best_reasoning = ""

    for r in range(6):
        for hold_combo in combinations(range(5), r):
            ev, reasoning = calculate_ev(hand, hold_combo)
            if ev > best_ev:
                best_ev = ev
                best_hold = hold_combo
                best_reasoning = reasoning

    return best_hold, best_reasoning

def calculate_ev(hand, hold_indices):
    held_cards = [hand.cards[i] for i in hold_indices]
    draw_count = 5 - len(held_cards)
    
    if draw_count == 0:
        return HAND_RANKINGS[evaluate_hand(hand)], "Keeping a made hand"

    remaining_deck = [Card(rank, suit) for rank in RANKS for suit in SUITS 
                      if Card(rank, suit) not in hand.cards]
    
    total_value = 0
    total_hands = 0
    
    for new_cards in combinations(remaining_deck, draw_count):
        new_hand = Hand()
        new_hand.cards = held_cards + list(new_cards)
        hand_value = HAND_RANKINGS[evaluate_hand(new_hand)]
        total_value += hand_value
        total_hands += 1
    
    ev = total_value / total_hands
    
    # Generate reasoning
    reasoning = generate_reasoning(hand, hold_indices, ev)
    
    return ev, reasoning

def generate_reasoning(hand, hold_indices, ev):
    held_cards = [hand.cards[i] for i in hold_indices]
    draw_count = 5 - len(held_cards)
    
    if draw_count == 0:
        return f"Keep all cards. You have a made hand: {evaluate_hand(hand)}."
    
    if draw_count == 5:
        return "Discard all cards. No viable holdings in this hand."
    
    held_ranks = [card.rank for card in held_cards]
    held_suits = [card.suit for card in held_cards]
    
    if len(set(held_suits)) == 1:
        if set(held_ranks) & set(['10', 'J', 'Q', 'K', 'A']):
            return f"Hold {draw_count} to a Royal Flush. High potential payoff."
        else:
            return f"Hold {draw_count} to a Flush. Good potential for improvement."
    
    if len(held_cards) == 4:
        if max(RANKS.index(r) for r in held_ranks) - min(RANKS.index(r) for r in held_ranks) <= 4:
            return "Hold four to an Outside Straight. Good drawing opportunity."
    
    if len(set(held_ranks)) < len(held_ranks):
        pairs = [rank for rank in set(held_ranks) if held_ranks.count(rank) > 1]
        if len(pairs) == 1:
            pair_rank = pairs[0]
            if pair_rank in ['J', 'Q', 'K', 'A']:
                return f"Hold the pair of {pair_rank}s. Guaranteed payout with potential for improvement."
            else:
                return f"Hold the low pair of {pair_rank}s. Potential to improve to Three of a Kind or better."
        elif len(pairs) == 2:
            return "Hold Two Pair. Guaranteed payout with potential to improve to Full House."
    
    high_cards = [card for card in held_cards if card.rank in ['J', 'Q', 'K', 'A']]
    if high_cards:
        return f"Hold {len(high_cards)} high card(s). Potential for Jacks or Better or better high pairs."
    
    return f"Hold {len(held_cards)} cards. This is the mathematically optimal play based on expected value calculations."

def main():
    st.title("Advanced Jack or Better Video Poker")
    
    if 'deck' not in st.session_state:
        st.session_state.deck = Deck()
    if 'hand' not in st.session_state:
        st.session_state.hand = Hand()
        for _ in range(5):
            st.session_state.hand.add_card(st.session_state.deck.draw())
    if 'credits' not in st.session_state:
        st.session_state.credits = 100
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
    
    st.write(f"Credits: {st.session_state.credits}")
    st.write("Your hand:", str(st.session_state.hand))
    
    help_requested = st.button("Get Hint")
    if help_requested:
        optimal_hold, reasoning = get_optimal_move(st.session_state.hand)
        st.write(f"Optimal move: Hold cards at positions {[i+1 for i in optimal_hold]}")
        st.write(f"Reasoning: {reasoning}")
    
    hold = [st.checkbox(f"Hold {card}", key=f"hold_{i}") for i, card in enumerate(st.session_state.hand.cards)]
    
    if st.button("Draw"):
        user_hold = [i for i, should_hold in enumerate(hold) if should_hold]
        st.session_state.last_action = user_hold
        
        for i, (card, should_hold) in enumerate(zip(st.session_state.hand.cards, hold)):
            if not should_hold:
                st.session_state.hand.cards[i] = st.session_state.deck.draw()
        
        hand_type = evaluate_hand(st.session_state.hand)
        payout = HAND_RANKINGS[hand_type]
        st.session_state.credits += payout
        
        st.write(f"New hand: {str(st.session_state.hand)}")
        st.write(f"Hand type: {hand_type}")
        st.write(f"Payout: {payout}")
        
        if not help_requested:
            optimal_hold, optimal_reasoning = get_optimal_move(st.session_state.hand)
            if set(user_hold) == set(optimal_hold):
                st.write("Your play was optimal!")
            else:
                st.write("Your play was not optimal. Here's the optimal play:")
                st.write(f"Optimal move: Hold cards at positions {[i+1 for i in optimal_hold]}")
                st.write(f"Reasoning: {optimal_reasoning}")
        
        if st.session_state.credits <= 0:
            st.write("Game over! You're out of credits.")
        else:
            if st.button("New Hand"):
                st.session_state.deck = Deck()
                st.session_state.hand = Hand()
                for _ in range(5):
                    st.session_state.hand.add_card(st.session_state.deck.draw())
                st.session_state.last_action = None
                st.experimental_rerun()

if __name__ == "__main__":
    main()
