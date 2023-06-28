import openai
# Set up OpenAI API key
openai.api_key = "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"
from services import check_submit, final_message, create_hyperlink, rate_items, get_dates


# Define function to generate response
def generate_response(conversation_history, prompt, f_p, preferences_f_p):
    ins_path = "sources/bot_instructor.txt"
    all_empty = all(value == [] for value in f_p.preferences.values())
    if all_empty:
        ins_path = "sources/bot_instructor_init.txt"
    submit = check_submit(prompt)
    if submit:
        f_p.num_of_passengers = int(prompt.split(' ')[1])
        ins_path = "sources/bot_submit.txt"
    with open(ins_path, 'r', encoding='utf-8') as file:
        checker = file.read()
    if not all_empty:
        dstn = ", ".join(str(item) for item in preferences_f_p["destinations"])
        sprt = ", ".join(str(item) for item in preferences_f_p["sports"])
        wthr = ", ".join(str(item) for item in preferences_f_p["weather"])
        act = ", ".join(str(item) for item in preferences_f_p["activities"])
        fd = ", ".join(str(item) for item in preferences_f_p["food"])
        tms = ", ".join(str(item) for item in preferences_f_p["teams"])
        checker = checker.replace("*DSTN*", dstn)
        checker = checker.replace("*SPRT*", sprt)
        checker = checker.replace("*WTHR*", wthr)
        checker = checker.replace("*ACT*", act)
        checker = checker.replace("*FD*", fd)
        checker = checker.replace("*TM*", tms)

    query = checker + prompt

    # Append prompt to conversation history
    conversation_history.append(query)

    # Concatenate conversation history into a single string
    conversation = "\n".join(conversation_history)

    # Generate response from GPT-3
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=conversation,
        temperature=0.5,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the text from the response and append it to the conversation history
    text = response.choices[0].text.strip()
    conversation_history.append(text)

    # update the flight_profile:
    rate_items(preferences_f_p, text)

    # Return the response text
    if not submit:
        return text
    else:
        f_p.num_of_passengers = prompt.split(' ')[1]
        num = int(f_p.num_of_passengers)
        if num > 12 or num < 1:
            return "Sorry, the number of passengers is invalid. Please try again with a number between 1 and 12"
        flights_urls, event_url = final_message(text, f_p)
        if flights_urls == "NOT FOUND":
            return "Sorry, something went wrong. Please try again"
        message = 'we have these flights for you:\n'
        for dst in flights_urls:
            text = f"\n{dst[0]}\n"
            hyperlink_text = f"{dst[0]}"
            message += create_hyperlink(text, hyperlink_text, dst[1], True)
        if event_url is not None:
            message += '\nAnd we have these events for you:\n' + create_hyperlink("events", "events", event_url, False)
        else:
            message += '\nBut we could not find events and activities that fits your preferences'
        return message


def set_date(message, f_p):
    dates = get_dates(message)
    if dates is None:
        return "sorry, these dates are invalid"
    f_p.date_from = dates[0]
    f_p.date_until = dates[1]
    message = f"Thank you! Your updated flight dates are as follows:\n" \
              f"Departure is between {dates[0].split('_')[0]} and {dates[0].split('_')[1]}\n" \
              f"Return is between {dates[1].split('_')[0]} and {dates[1].split('_')[1]}"
    return message


def response_bot(messages, message, f_p):
    dic_flight_preferences = f_p.preferences
    try:
        date_message = message.split(' ')[0]
        if date_message == 'DATES:':
            response = set_date(message, f_p)
            return response, dic_flight_preferences
        conversation_history = [c.content for c in messages]
        response = generate_response(conversation_history, message, f_p, dic_flight_preferences)
        return response, dic_flight_preferences
    except Exception as e:
        error_message = "Apologies, but an error occurred while processing your request. Please try again."
        return error_message, dic_flight_preferences
