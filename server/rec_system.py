from collections import Counter
from services import get_flights, create_hyperlink, get_correct_link_activity
import jellyfish
from models import FlightProfile, Conversation
from database import db


# this class it for using the functions from service.py that requries these fields from f_p:
class Dates:
    def __init__(self, date_from="anytime", date_until="anytime", num_of_passengers=2):
        self.date_from = date_from
        self.date_until = date_until
        self.num_of_passengers = num_of_passengers


def remove_user_flight_profiles(user_flight_profiles, all_flight_profiles):
    user_flight_profile_ids = {fp.flight_profile_id for fp in user_flight_profiles}
    filtered_flight_profiles = [fp for fp in all_flight_profiles if fp.flight_profile_id not in user_flight_profile_ids]
    return filtered_flight_profiles


def flight_profile_to_string(flight_profile):
    preference_strings = []
    preferences = flight_profile.preferences

    for key, values in preferences.items():
        if values:
            values_str = ", ".join(values)
            preference_strings.append(f"{key.capitalize()}: {values_str}")

    return "\n".join(preference_strings)


def compute_similarity(profile1, profile2):
    # Convert flight profile strings to lowercase for case-insensitive comparison
    profile1 = profile1.lower()
    profile2 = profile2.lower()

    # Use a distance metric (e.g., Jaro-Winkler, Levenshtein) to compute the similarity score
    score = jellyfish.jaro_winkler(profile1, profile2)
    return score


def find_similar_profiles(user_flight_profiles, all_flight_profiles):
    similar_profiles = []

    for user_f_p in user_flight_profiles:
        user_f_p_string = flight_profile_to_string(user_f_p)
        for f_p in all_flight_profiles:
            f_p_string = flight_profile_to_string(f_p)
            similarity_score = compute_similarity(user_f_p_string, f_p_string)
            similar_profiles.append((user_f_p, f_p, similarity_score))

    similar_profiles.sort(key=lambda x: x[2], reverse=True)  # Sort profiles by similarity score in descending order
    return similar_profiles


def is_all_users_empty(all_flight_profiles):
    # Check if there are no other users except the current user
    if len(all_flight_profiles) < 1:
        return True

    # Check if all preference lists in all flight profiles are empty
    for flight_profile in all_flight_profiles:
        preferences = flight_profile.preferences
        for preference_list in preferences.values():
            if len(preference_list) > 0:
                return False

    return True


def generate_links(dst, categories, flag):
    dates = Dates()
    dst = dst.split(',')[0].strip()
    flight_url = get_flights(dst, dates)[0]
    flight_link = create_hyperlink(dst, dst, flight_url[1], True)
    event_url = get_correct_link_activity(dates, dst, categories)
    event_link = create_hyperlink("events", "events", event_url, False)
    if event_link is None:
        event_link = "No relevant events"
    if flag == "empty_db":
        message = f"Welcome new friend! Here are some recommended flights and events for you!<br>Flight to: " \
                  f"{flight_link}<br>And some events in the area: {event_link}"
        return message
    elif flag == "new_user":
        message = f"Welcome new friend! Here are the most popular flights and events of all of" \
                  f" our users for you!<br>Flight to: " \
                  f"{flight_link}<br>And some events in the area: {event_link}"
        return message
    elif flag == "full_db":
        message = f"Welcome back dear friend! according to your preferences, you may like this flight" \
                  f":<br>{flight_link}<br>" \
                  f"and these events: {event_link}"
        return message
    else:
        message = f"Welcome dear friend! our system found this recommendation for you" \
                  f":<br>{flight_link}<br>" \
                  f"and these events: {event_link}"
        return message



def first_recommendation_empty_db(flag):
    categories = [" ", " :soccer", " :Entertainment", " :Barcelona"]
    message = generate_links("Barcelona", categories, flag)
    return message


def first_recommendation_not_empty_db(all_flight_profiles):
    preference_counter = {
        'destinations': Counter(),
        'sports': Counter(),
        'weather': Counter(),
        'activities': Counter(),
        'food': Counter(),
        'teams': Counter()
    }
    # Iterate over all flight profiles and update the preference counter
    for flight_profile in all_flight_profiles:
        preferences = flight_profile.preferences
        for key, values in preferences.items():
            modified_values = [value.capitalize() for value in values]
            preference_counter[key].update(modified_values)

    top_preferences = {}
    for key, counter in preference_counter.items():
        if counter:
            top_preferences[key] = counter.most_common(1)[0][0]
        else:
            top_preferences[key] = None
    categories = []
    for key in top_preferences:
        if top_preferences[key] is not None:
            categories.append(" :" + top_preferences[key])
        else:
            categories.append(":")
    message = generate_links(top_preferences["destinations"], categories, "new_user")
    return message


def recommendation_full_db(top_flight_profiles, user_flight_profiles):
    most_common_preferences = []

    # Define the order of preferences
    preference_order = ['destinations', 'sports', 'weather', 'activities', 'food', 'teams']

    # Iterate through the preference order
    for preference in preference_order:
        preference_values = []

        # Check if the preference is not already in any of the user flight profiles' preferences
        if not any(preference in fp.preferences.values() for fp in user_flight_profiles):
            # Iterate through the top flight profiles
            for flight_profile in top_flight_profiles:
                preferences = flight_profile[1].preferences

                # Check if the preference is not already in any of the user flight profiles' preferences
                if preferences[preference] not in [fp.preferences[preference] for fp in user_flight_profiles]:
                    preference_values.extend(preferences[preference])

        if preference_values:
            most_common_preferences.append(f"{preference.capitalize()}: {', '.join(preference_values)}")
        else:
            most_common_preferences.append(f"{preference.capitalize()}:")

    # If the most_common_preferences list is empty, extract the most common preferences from the user flight profiles
    if not most_common_preferences:
        all_user_preferences = [fp.preferences for fp in user_flight_profiles]
        all_user_preferences_values = [value for preferences in all_user_preferences for value in preferences.values()]
        counter = Counter(all_user_preferences_values)
        most_common_preferences = [f"{preference.capitalize()}: {value}" for preference, value in
                                   counter.most_common(len(preference_order))]

    dst = most_common_preferences[0].split(':')[1].strip()
    message = generate_links(dst, most_common_preferences, "full_db")
    return message


def get_recommendation(user_id):
    try:
        # Retrieve the flight profile of the current user
        user_conversations = Conversation.query.filter_by(email=user_id).all()
        user_flight_profiles = [c.flight_profile for c in user_conversations]

        # get all the user preferences:
        entire_user_pref = {"destinations": [],
                            "sports": [],
                            "weather": [],
                            "activities": [],
                            "food": [],
                            "teams": []}

        for flight_profile in user_flight_profiles:
            preferences = flight_profile.preferences

            # Update each key in entire_user_pref with corresponding items
            for key in entire_user_pref:
                entire_user_pref[key].extend(preferences.get(key, []))

        # Get all flight profiles from the database
        all_flight_profiles = FlightProfile.query.filter(FlightProfile.conversation_id != user_id).all()
        all_flight_profiles = remove_user_flight_profiles(user_flight_profiles, all_flight_profiles)
        # check if the user has nothing in the db yet
        single_user_all_empty = all(not entire_user_pref[key] for key in entire_user_pref)

        # check if there are no others users in the db, or there but with no any preferences
        all_users_all_empty = is_all_users_empty(all_flight_profiles)

        if all_users_all_empty:
            recommendation = first_recommendation_empty_db("empty_db")
            return recommendation
        else:  # we have some data to count on in the db
            if single_user_all_empty:
                recommendation = first_recommendation_not_empty_db(all_flight_profiles)
                return recommendation
            else:
                similar_f_p = find_similar_profiles(user_flight_profiles, all_flight_profiles)
                total_f_p = len(similar_f_p)  # Total number of flight profiles
                min_percentage = 0.2  # Minimum percentage to consider
                # Calculate the percentage based on the total number of profiles
                percentage = min(min_percentage, 1.0 / total_f_p)
                # Calculate the number of flight profiles to include based on the calculated percentage
                num_profiles = int(total_f_p * percentage)
                # Get the top flight profiles based on the calculated number
                top_flight_profiles = similar_f_p[:num_profiles]
                recommendation = recommendation_full_db(top_flight_profiles, user_flight_profiles)
                return recommendation

    except Exception as e:
        recommendation = first_recommendation_empty_db("rec_error_handle")
        return recommendation




