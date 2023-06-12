import csv
import json
import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
path_to_used_organizations = os.getenv("USED_ORGANIZATIONS_PATH")
necessary_equip = os.getenv("NECESSARY_EQUIP")
ORGANIZATION_TO_GENERATE = 10
RELEVANT_RATE = 75


def get_organization_info() -> str:
    with open(path_to_used_organizations, "r") as f:
        orgs = f.readlines()
    orgs = [org.strip() for org in orgs]
    return "\n".join(orgs)


def get_equip() -> str:
    with open(necessary_equip) as json_file:
        json_data = json.load(json_file)
    json_string = json.dumps(json_data)
    return json_string


BLACKLIST = get_organization_info()
EQUIPMENT = get_equip()


def get_response():
    print("started")
    system = f"""
        You are helpful assistant that finds international volunteering organizations for me.
        Don`t include these organizations in your response: {BLACKLIST}
"""
    prompt = f"""
    Your task is to create a comprehensive directory of volunteering organizations in your area that can help 
    to alleviate the consequences of the hydroelectric power plant explosion.
    The desired format for each organization is as follows:
    
    N: (Name of the organization)
    W: (Website of the organization)
    C: (Contact information for the organization in the next format: 1 (555) 555-5555, jhondoe@gmail.com)
    S: (A brief description of the organization's mission and services)
    Your goal is to generate a well-structured list of volunteering organizations that have not been contacted yet and are suitable for Eastern Europe. Your response should include at least {ORGANIZATION_TO_GENERATE} organizations and should strictly adhere to the specified format. Please only include organizations that actually exist and provide real, working website links (base URLs, not specific pages).

    
    Additionally, you have been provided with a list of EQUIPMENT: {EQUIPMENT} that may be useful for volunteering organizations.
    I have already contacted some organizations, which are listed in the BLACKLIST: {BLACKLIST}.
    Please do not include any of these organizations in your response.

    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": system},
        ],
        temperature=0.0,
        max_tokens=5000,
        timeout=1000,
    )

    result = response["choices"][0]["message"]["content"].strip(" \n")
    print("finished")
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
        "Relevance Score"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(organizations)


def write_names_to_file(filename, links):
    with open(filename, "a") as f:
        for link in links:
            f.write(link + "\n")


def extract_names_from_csv(csv_filename):
    links = []
    with open(csv_filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            link = row["Organization Name"]
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


def check_for_relevant(list_to_check: list[dict]):
    print("Start checking for relevant organizations")
    prompt = f"""
    Given a list of organizations and a blacklist, generate a response that checks whether the organizations entered by 
    the user are not in their blacklist. Additionally, determine the relevance of these organizations in helping with 
    the user's list of items. Lastly, ensure that these organizations are capable of providing assistance to citizens of Ukraine.
    
    Blacklist: {BLACKLIST}
    
    List of Organizations: {list_to_check}
    
    List of Items: {EQUIPMENT}
    
    User's Nationality: Ukrainian
    
    Please assign a relevance score from 1 to 100 to each organization based on how relevant they are to the user's needs.
    Do not modify the structure of the organization list in the response save full info and simply add score to each.
    And simply return the list of organizations with their scores without any words.
    """

    system = "Act as professional assistant that checks for relevant organizations."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=3500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1,
        timeout=1000,
    )

    result = response["choices"][0]["message"]["content"].strip(" \n")

    print("Finished checking for relevant organizations")

    return result


def sort_and_filter_organizations(organizations):
    sorted_organizations = sorted(organizations, key=lambda x: x["Relevance Score"], reverse=True)
    filtered_organizations = [org for org in sorted_organizations if org["Relevance Score"] >= RELEVANT_RATE]
    return filtered_organizations


def main():
    data = get_response()
    organizations = parse_organization_data(data)
    checks_organization = check_for_relevant(organizations)
    organizations = sort_and_filter_organizations(eval(checks_organization))
    write_organizations_to_csv("organizations.csv", organizations)
    names = extract_names_from_csv("organizations.csv")
    write_names_to_file(path_to_used_organizations, names)
