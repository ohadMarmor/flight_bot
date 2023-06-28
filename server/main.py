from selenium import webdriver


def check_text_in_webpage(url, target_text):

    message = ''

    driver = webdriver.Chrome()  # You will need to have the Chrome driver executable in your system PATH
    driver.get(url)

    webpage_content = driver.page_source

    if target_text in webpage_content:
        message = "I'm, sorry, but there is no events for you in the dates you asked for"
    else:
        message = url

    driver.quit()
    return url


# Example usage
url = "https://www.sportsevents365.com/events/?autosuggest_who=Entertainment&autosuggest_where=Paris%2CFrance" \
      "&datepicker_from=09%2F06%2F2023&datepicker_until=10%2F06%2F2023&submit=&suggestid_where=&suggestid_who" \
      "=sporttypes_1023&who_index=-1&where_index=-1&entertainmentSearch=0"
target_text = "Your search did not return any results."


# function to generate url - if data not exist put ""
def generate_url(city, country, team, event, d_from, d_to):
    # connect format city, country
    if city != "" or country != "":
        if city != "" and country != "":
            f_city_country = city + "%2C+" + country
        elif country == "":
            print("TODO - add function to get country by city")
            f_city_country = ""
        else:
            f_city_country = country
    else:
        f_city_country = ""
    # check if link for sport or other entertainment
    f_event = event
    if event == "Entertainment":
        f_enter = 1
    else:
        f_enter = 0
        if team != "":
            if event != "":
                f_event = team + "%2C+" + event
            else:
                f_event = team
    url = f"https://www.sportsevents365.com/events/?autosuggest_who={f_event}&autosuggest_where={f_city_country}" \
          f"&datepicker_from={d_from}&datepicker_until={d_to}&entertainmentSearch={f_enter}"
    return url

# city, country, team:
# ("Madrid", "Spain", "Real+Madrid", "", "20/06/2023", "10/07/2023")

# city, country:
# ("Madrid", "Spain", "", "", "20/06/2023", "10/07/2023")

# country:
# ("", "Spain", "", "", "20/06/2023", "10/07/2023")

# city, country, Entertainment:
# ("Madrid", "Spain", "", "Entertainment", "20/06/2023", "10/07/2023")


# Example usage:
bad_url = generate_url("Madrid", "Spain", "Real Madrid", "", "20/06/2023", "10/07/2023")
# print("Generated bad URL:", bad_url)

check_text_in_webpage(bad_url, target_text)
# check_text_in_webpage(good_url, target_text)
