import csv
import json
import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
path_to_used_organizations = os.getenv("USED_ORGANIZATIONS_PATH")
necessary_equip = os.getenv("NECESSARY_EQUIP")
ORGANIZATION_TO_GENERATE = 5

def get_organization_info() -> str:
    with open(path_to_used_organizations, "r") as f:
        orgs = f.readlines()
    orgs = [org.strip() for org in orgs]
    return "\n".join(orgs)


def get_equip() -> str:
    equip = json.loads(open(necessary_equip, "r").read())
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

Contacted Organizations STRICTLY DON`T ADD THESE ORGANIZATIONS IN YOUR RESPONSE!:
{get_organization_info()}

Equipment that may be useful for volunteering organizations:
{get_equip()}

Instructions:
Please generate a list of volunteering organizations in the specified format. Include at least {ORGANIZATION_TO_GENERATE} organizations in your response. Do not include any organizations that are already present in the list of contacted organizations.


Your response should be a well-structured list of volunteering organizations that have not been contacted yet and suitable for Ukraine.
ANSWER STRICTLY STRUCTURED AS FOLLOWS:
N:
W:
Contacts:
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


def generate_message(company_name, specialization):
    personal_name = os.getenv("PERSONAL_NAME", "<YOUR_NAME>")
    print(personal_name, "NAME")
    example = f"""
        My name is personal name, and I'm a volunteer with the Ukrainian organization "Тарілка" and "А що зробив ти?".
        I wanted to reach out and inform you about the dire situation in the Kherson region, where we are currently providing assistance.
        Due to the ongoing acts of Russian terrorism, the locals and rescuers are facing tremendous hardships.
        In light of this, we have set up an aid station in Kherson to support those in need. The people there require
        immediate help, particularly in the form of {get_equip()}
        I would sincerely appreciate it if you could consider extending your support to our cause. Every contribution,
        no matter how small, can make a significant difference in the lives of those affected. If you are willing and 
        able to assist us, please kindly let us know. Your help would mean the world to the people of Kherson.
        Thank you for your time and consideration.
        Warm regards,
        Andrii
    """

    system = """
        You are helpful assistant that writes messages to volunteering organizations.
    """

    prompt = f"""
        My name is {personal_name}, and I'm a volunteer with the Ukrainian organization "Тарілка" and "А що зробив ти?".
        I wanted to reach out and inform you about the dire situation in the Kherson region,
        where we are currently providing assistance.
        Due to the ongoing acts of Russian terrorism, the locals and rescuers are facing tremendous hardships.
        Your letter conveys a strong sense of concern and danger faced by the residents of the Kherson region due to acts of terrorism conducted by Russia.
        You ask for support and assistance for people who are experiencing great hardship. You list in detail the items needed and note that even small contributions can make a huge difference in the lives of the victims.
        Your appeal is grateful and full of hope for help.
        INFO ABOUT ORGANIZATIONS:
        NAME: {company_name}
        SPECIALIZATION:{specialization}
    """  # EXAMPLE OF LETTER ->>> {example} <<<- EXAMPLE OF LETTER

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=4500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        timeout=1000,
    )

    result = response["choices"][0]["message"]["content"].strip(" \n")

    return result


def main():
    data = get_response()
    organizations = parse_organization_data(data)
    write_organizations_to_csv("organizations.csv", organizations)
    links = extract_links_from_csv("organizations.csv")
    write_links_to_file(path_to_used_organizations, links)
