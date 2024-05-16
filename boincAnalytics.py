import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def scrape_data():
    base_url = "http://ctmc.isinyour.skin:8000/fitcrack/show_host_detail.php?hostid="
    days_count = {}
    host_id = 1
    last_successful_host_id = 0
    valid_host_count = 0
    bad_response_count = 0

    while True:
        url = f"{base_url}{host_id}"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for "Unable to handle request" heading
            h2_heading = soup.find('h2')
            if h2_heading and h2_heading.text.strip() == "Unable to handle request":
                bad_response_count += 1
                if bad_response_count >= 5:
                    break
            else:
                bad_response_count = 0
                last_contacted_date = None

                # Find all <td> elements
                td_elements = soup.find_all('td')

                # Loop through <td> elements to find the required data
                for i in range(len(td_elements)):
                    if td_elements[i].text.strip() == "Last contact":
                        last_contacted_date = td_elements[i + 1].text.strip()

                # Calculate days since last contact if date was found
                if last_contacted_date:
                    last_contact_date_obj = datetime.strptime(last_contacted_date, "%d %b %Y").replace(
                        tzinfo=timezone.utc)
                    current_date = datetime.now(timezone.utc)
                    days_since_last_contact = (current_date - last_contact_date_obj).days

                    # Increment the count for the corresponding day
                    if days_since_last_contact <= 10:
                        if days_since_last_contact in days_count:
                            days_count[days_since_last_contact] += 1
                        else:
                            days_count[days_since_last_contact] = 1
                    else:
                        if 10 in days_count:
                            days_count[10] += 1
                        else:
                            days_count[10] = 1

                # Update the last successful host ID
                last_successful_host_id = host_id
                valid_host_count += 1

        else:
            bad_response_count += 1
            if bad_response_count >= 5:
                break

        host_id += 1

    return days_count, last_successful_host_id, valid_host_count


# Scrape the data
days_count, last_successful_host_id, valid_host_count = scrape_data()

# Print the aggregated data
if not days_count:
    print("No data found.")
else:
    for days in range(11):
        if days < 10:
            count = days_count.get(days, 0)
            print(f"{days} Days since last contact: {count} hosts")
        else:
            count = days_count.get(10, 0)
            print(f"10+ Days since last contact: {count} hosts")

# Print the highest host ID reached and the number of valid hosts
print(f"Highest host ID reached: {last_successful_host_id}")
print(f"Total number of valid hosts: {valid_host_count}")
