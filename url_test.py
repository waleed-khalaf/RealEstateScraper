from RightmoveScraper import *

location_identifier = generate_url("glasgow")

csv_results = []
for page in range(1, 42):
    page_index = 24 * page
    url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={location_identifier}&' \
          f'index={page_index}&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords='
    response = fetch_html(url)
    data = site_parser(response)
    csv_results.append(data)

write_to_csv(csv_results)
