import csv
import json
import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
path_to_used_organizations = os.getenv("USED_ORGANIZATIONS")
path_to_necessary_equip = os.getenv("NECESSARY_EQUIP")


def get_organization_info() -> str:
    with open(path_to_used_organizations, "r") as f:
        orgs = f.readlines()
    orgs = [org.strip() for org in orgs]
    return "\n".join(orgs)


def get_equip() -> str:
    equip = json.loads(open(path_to_necessary_equip, "r").read())
    return ", ".join(equip)


def get_response():
    system = """
        You are helpful assistant that finds international volunteering organizations for me.
"""
    prompt = f"""
    You are working on creating a comprehensive directory of volunteering organizations in your area. Your goal is to generate a list of volunteering organizations with the following format:

N:
W:
C:
S:

You also have a list of organizations that you have already contacted. Please provide the list of contacted organizations as follows:

Contacted Organizations DON`T ADD THESE ORGANIZATIONS IN YOUR RESPONSE:
{get_organization_info()}

Equipment that may be useful for volunteering organizations:
{get_equip()}

Instructions:
Please generate a list of volunteering organizations in the specified format. Include at least 2 organizations in your response. Do not include any organizations that are already present in the list of contacted organizations.


Your response should be a well-structured list of volunteering organizations that have not been contacted yet and suitable for Ukraine.
ANSWER STRICTLY STRUCTURED AS FOLLOWS:
N:
W:
C:
S:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=4000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        timeout=1000,
    )

    result = response["choices"][0]["message"]["content"].strip(" \n")
    print(result)

    return result


def parse_organization_data(data):
    organizations = []
    lines = data.strip().split("\n\n")

    for line in lines:
        org_data = line.split("\n")

        organization = {
            "Organization Name": org_data[0].split(": ")[1].strip(),
            "Website": org_data[1].split(": ")[1].strip(),
            "Contact Information": org_data[2].split(": ")[1].strip(),
            "Specialization": org_data[3].split(": ")[1].strip(),
        }

        organizations.append(organization)

    return organizations


def write_organizations_to_csv(filename, organizations):
    fieldnames = [
        "Organization Name",
        "Website",
        "Contact Information",
        "Specialization",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(organizations)


def write_links_to_file(filename, links):
    with open(filename, "a") as f:
        for link in links:
            f.write(link + "\n")


def extract_links_from_csv(csv_filename):
    links = []
    with open(csv_filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            link = row["Website"]
            links.append(link)
    return links


def main():
    data = get_response()
    organizations = parse_organization_data(data)
    write_organizations_to_csv("organizations.csv", organizations)
    links = extract_links_from_csv("organizations.csv")
    write_links_to_file(path_to_used_organizations, links)

