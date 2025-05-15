import streamlit as st

def initialize_session_state():
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'current_rater' not in st.session_state:
        st.session_state.current_rater = 0
    if 'ratings' not in st.session_state:
        st.session_state.ratings = []  # List of dictionaries


def start_game():
    st.session_state.game_started = True
    st.session_state.ratings = []


def save_ratings(new_ratings_list):
    st.session_state.ratings.extend(new_ratings_list)
    st.session_state.current_rater += 1


def calculate_averages():
    player_totals = {}
    player_counts = {}

    for entry in st.session_state.ratings:
        rated = entry['Rated Player']
        if rated not in player_totals:
            player_totals[rated] = {cat: 0 for cat in st.session_state.categories}
            player_counts[rated] = {cat: 0 for cat in st.session_state.categories}
        for cat in st.session_state.categories:
            player_totals[rated][cat] += entry[cat]
            player_counts[rated][cat] += 1

    averages = {}
    for player in player_totals:
        averages[player] = {}
        for cat in st.session_state.categories:
            if player_counts[player][cat] > 0:
                averages[player][cat] = player_totals[player][cat] / player_counts[player][cat]
            else:
                averages[player][cat] = None
    return averages


def write_individual_ratings_to_file():
    with open("result.txt", "a", encoding="utf-8") as file:
        file.write("===== INDIVIDUAL RATINGS =====\n")
        for rater in st.session_state.players:
            file.write(f"\n🧑‍⚖️ {rater}'s ratings for others:\n")
            for entry in st.session_state.ratings:
                if entry['Rater'] == rater:
                    rated = entry['Rated Player']
                    file.write(f"  → {rated}:\n")
                    for cat in st.session_state.categories:
                        file.write(f"     - {cat}: {entry[cat]}/10\n")


def main():
    initialize_session_state()
    st.title("👥 Anonymous Group Rating Game 👥")

    if not st.session_state.game_started:
        with st.form("game_setup"):
            players = st.text_area("Enter player names (one per line)", "").split('\n')
            categories = st.text_area("Enter rating categories (one per line)", "Beauty\nCharisma\nPhysique").split('\n')

            if st.form_submit_button("Start Game"):
                players = [p.strip() for p in players if p.strip()]
                categories = [c.strip() for c in categories if c.strip()]
                if len(players) < 2:
                    st.error("Need at least 2 players!")
                    return
                if not categories:
                    st.error("Need at least 1 category!")
                    return

                st.session_state.players = players
                st.session_state.categories = categories
                start_game()
                st.rerun()

    else:
        if st.session_state.current_rater < len(st.session_state.players):
            current_player = st.session_state.players[st.session_state.current_rater]
            st.subheader(f"👋 {current_player}'s Turn")
            st.write("Rate other players anonymously (1-10):")

            ratings = {}
            with st.form("rating_form"):
                for player in st.session_state.players:
                    if player != current_player:
                        st.markdown(f"**Rate {player}**")
                        for category in st.session_state.categories:
                            ratings[f"{player}_{category}"] = st.slider(
                                f"{category} - {player}",
                                1, 10, 5,
                                key=f"{current_player}_{player}_{category}"
                            )

                if st.form_submit_button("Submit Ratings"):
                    formatted_ratings = []
                    for player in st.session_state.players:
                        if player != current_player:
                            player_rating = {
                                'Rated Player': player,
                                'Rater': current_player
                            }
                            for category in st.session_state.categories:
                                player_rating[category] = ratings[f"{player}_{category}"]
                            formatted_ratings.append(player_rating)

                    save_ratings(formatted_ratings)
                    st.rerun()

        else:
            st.subheader("🏆 Final Results 🏆")
            avg_scores = calculate_averages()

            for player in st.session_state.players:
                st.markdown(f"### {player}'s Scores")
                for category in st.session_state.categories:
                    score = avg_scores[player].get(category)
                    if score is not None:
                        st.metric(category, f"{score:.1f}/10")
                    else:
                        st.metric(category, "N/A")

            write_individual_ratings_to_file()

            if st.button("Play Again"):
                st.session_state.clear()
                st.rerun()


if __name__ == "__main__":
    main()
