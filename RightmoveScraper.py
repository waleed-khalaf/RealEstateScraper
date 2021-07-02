# CURRENTLY EXCLUSIVELY SEARCHES FOR PROPERTIES IN GLASGOW. NEED TO FIND WAY TO DYNAMICALLY GENERATE URL FOR OTHER
# LOCATIONS
# TODO: Find full post code for property then use that to find price of sold properties for DUV
# TODO: Do analysis and write to excel file using openpyxl to automate

import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import csv


# TODO: find a way to dynamically generate the locationIdentifier parameter in the url to be able to search
#  for specific cities that can be entered as an argument for the `fetch_html` function.
# Data structure for dynamically generated urls to feed into `fetch_html()` ?


def generate_url(location) -> str:
    """
    Generates urls of city to be searched using the rightmove api and the locationIdentifier parameter to dynamically
    generate the required url by taking in either a city name or post code as an argument. 
    :param location: Name of city or post code to be searched.
    :return: url string
    """

    region_endpoint_url = "https://www.rightmove.co.uk/typeAhead/uknostreet/"
    count = 0
    for char in location.upper():
        if count == 2:
            region_endpoint_url += '/'
            count = 0
        region_endpoint_url += char
        count += 1

    region_response = requests.get(region_endpoint_url).json()
    searched_locations = region_response['typeAheadLocations']

    for entry in searched_locations:
        confirm_location = input(f"Is {entry['displayName']} the search entry you are looking for ? Enter Y/N:").upper()
        if confirm_location == 'Y':
            region_code = entry['locationIdentifier']
            return region_code
        else:
            continue


def fetch_html(parsed_url):
    """
    Uses the requests module to return a response from a constructed a www.rightmove.co.uk entered as an
    argument.
    :param parsed_url: url string needed to make https request.
    :return: response object from get request to city listings on rightmove.co.uk.
    """
    try:
        rm_response = requests.get(parsed_url)
        rm_response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return
    else:
        print(f"Success | Status Code: {rm_response.status_code}")
        return rm_response


def site_parser(response) -> list:
    """
    Makes 'soup' out of html to parse and scrapes relevant data and returns a list of dictionaries containing the info.
    :param response: response from http request.
    :return: list of dictionaries
    """
    # TODO: Exception handling if request doesn't get html page because it's out of range.
    html = response.content
    content = BeautifulSoup(html, 'lxml')
    titles = [titles.text.strip('\n ') for titles in content.find_all('h2', {'class': 'propertyCard-title'})]
    addresses = [addresses['content'] for addresses in content.find_all('meta', {'itemprop': 'streetAddress'})]
    descriptions = [descriptions.text.strip('\n') for descriptions in
                    content.find_all('div', {'class': 'propertyCard-description'})]
    prices = [prices.text.strip(' ') for prices in content.find_all('div', {'class': 'propertyCard-priceValue'})]
    # TODO: Extract date only. If no date available need to find someway to skip.
    date_added = [date_added.text for date_added in
                  content.find_all('span', {'class': 'propertyCard-contactsAddedOrReduced'})]
    sellers = [sellers.text.strip(' by') for sellers in
               content.find_all('span', {'class': 'propertyCard-branchSummary-branchName'})]
    property_urls = [f'www.rightmove.co.uk{property_urls["href"]}' for property_urls in
                     content.find_all('a', {'class': 'propertyCard-link'})]

    # List of dictionaries made to contain all the data for each property in a single dictionary each.
    results = []
    for index in range(1, len(titles)):
        data_dict = {
            'Title': titles[index],
            'Address': addresses[index],
            'Description': descriptions[index],
            'Price': prices[index],
            'Date added': date_added[index],
            'Seller': sellers[index],
            'Url': property_urls[index]
        }
        results.append(data_dict)

    return results


# TODO: Exception handling if file isn't there.
def write_to_csv(data_to_write: list):
    """
    Takes in list of data and then writes it to csv file called RealEstateData.csv.
    :param data_to_write: list that is to be written to csv
    """
    with open('RealEstateData.csv', 'w') as csv_file:
        fieldnames = data_to_write[0][0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for _ in data_to_write:
            for row in _:
                writer.writerow(row)
    print("Stored results to 'RealEstateData.csv'")


# --------------------CONTROL FLOW OF PROGRAM--------------------:

# GENERATE URL (DYNAMICALLY GENERATED OR HARD CODED)
# PASS URL INTO `fetch_html` AS AN ARGUMENT
# PASS OUTPUT OF `fetch_html` INTO `site_parser'

# EXPORT RESULTS OF SCRAPING TO CSV

# csv_results = []
# # Scraping the results from the search and saving to csv file
# for page in range(1, 42):
#     page_index = 24 * page
#     url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E550&' \
#           f'index={page_index}&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords='
#     response = fetch_html(url)
#     data = site_parser(response)
#     csv_results.append(data)
#
#
# write_to_csv(csv_results)
