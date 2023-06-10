import csv
import json
import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_organization_info() -> list[str]:
    with open("orgs.csv", "r") as f:
        orgs = f.readlines()
    orgs = [org.strip() for org in orgs]
    return orgs


def get_equip():
    equip = json.loads(open("equip.json", "r").read())
    return equip


def get_response():
    system = '''
        You are helpful assistant that finds international volunteering organizations for me.
'''
    # prompt = f"""
    #     dont add these organizations in your response: {get_organization_info()}.
    #     Return me organizations that may be have following equipment: {get_equip()}.
    #     Write at least 5 organizations.
    #     You should give me following information about organization:
    #     Назва організації
    #     Сайт
    #     Контактні дані
    #     Спеціалізація
    # """

    prompt = f"""
    You are working on creating a comprehensive directory of volunteering organizations in your area. Your goal is to generate a list of volunteering organizations with the following format:

N:
W:
C:
S:

You also have a list of organizations that you have already contacted. Please provide the list of contacted organizations as follows:

Contacted Organizations:
{get_organization_info()}

Instructions:
Please generate a list of volunteering organizations in the specified format. Include at least 60 organizations in your response. Do not include any organizations that are already present in the list of contacted organizations.

Remember to adhere to the table format:
Назва організації (Organization Name):
Сайт (Website):
Контактні дані (Contact Information):
Спеціалізація (Specialization):

Your response should be a well-structured list of volunteering organizations that have not been contacted yet and suitable for Ukraine.
    """

    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.0,
        max_tokens=7000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        timeout=1000
    )

    result = response['choices'][0]['message']['content'].strip(' \n')
    print(result)

    return result


def parse_organization_data(data):
    organizations = []
    lines = data.strip().split('\n\n')

    for line in lines:
        org_data = line.split('\n')

        organization = {
            'Organization Name': org_data[0].split(': ')[1].strip(),
            'Website': org_data[1].split(': ')[1].strip(),
            'Contact Information': org_data[2].split(': ')[1].strip(),
            'Specialization': org_data[3].split(': ')[1].strip()
        }

        organizations.append(organization)

    return organizations


def write_organizations_to_csv(filename, organizations):
    fieldnames = ['Organization Name', 'Website', 'Contact Information', 'Specialization']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(organizations)


def main():
    result = parse_organization_data(get_response())
    write_organizations_to_csv('organizations.csv', result)


if __name__ == "__main__":
    main()
