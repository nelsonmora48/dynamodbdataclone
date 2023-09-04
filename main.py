#!/usr/bin/env python3
import boto3
from simple_term_menu import TerminalMenu

profile = {}
profile["src"] = ""
profile["dst"] = ""
src_dynamdb_client = ""
dst_dynamdb_client = ""


def select_menu(options: list):
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    print(f"You have selected {options[menu_entry_index]}!")
    print()
    return options[menu_entry_index]


def get_profile(label: str):
    cli_input = (
        str(
            input(
                f"Set the name of the [{label}] profile (default: {profile[label]}): "
            )
        )
        .lstrip()
        .rstrip()
    )
    if cli_input == "":
        return profile[label]
    return cli_input


def check_profile(profile):
    session = boto3.Session(profile_name=profile)
    dynamdb_client = session.client("dynamodb")


def select_dynamo_table(profile: str):
    session = boto3.Session(profile_name=profile)
    dynamdb_client = session.client("dynamodb")
    paginator = dynamdb_client.get_paginator("list_tables")
    pages = paginator.paginate()
    tables = []
    for page in pages:
        for table in page["TableNames"]:
            tables.append(table)
    return select_menu(tables)


def confirm(message: str):
    resp = ""
    while resp not in ["y", "Y", "n", "N"]:
        resp = input(f"{message} (y/n): ")

    return resp in ["y", "Y"]


def execute_migration(src_profile, dst_profile, src_table, dst_table):
    src_session = boto3.Session(profile_name=src_profile)
    dst_session = boto3.Session(profile_name=dst_profile)
    src_dynamdb_client = src_session.client("dynamodb")
    dst_dynamdb_client = dst_session.client("dynamodb")
    src_paginator = src_dynamdb_client.get_paginator("scan")
    pages = src_paginator.paginate(TableName=src_table)
    items_quantity = 0
    put_requests = []
    for page in pages:
        for item in page["Items"]:
            put_requests.append({"PutRequest": {"Item": item}})
            items_quantity += 1
            if items_quantity % 25 == 0:
                response = dst_dynamdb_client.batch_write_item(
                    RequestItems={dst_table: put_requests}
                )
                put_requests = []
                if "UnprocessedItems" in response:
                    if response["UnprocessedItems"] != {}:
                        print(response)
                print(f"{items_quantity} items copied", end="\r")

    # Insert Final
    response = dst_dynamdb_client.batch_write_item(
        RequestItems={dst_table: put_requests}
    )
    if "UnprocessedItems" in response:
        if response["UnprocessedItems"] != {}:
            print(response)
    print(f"{items_quantity} items copied", end="\r")


def save_2disk(item: str, value: str):
    file_object = open(item, "w+")
    file_object.write(value)
    file_object.close()


def load_from_disk(item: str):
    try:
        file_object = open(item, "r")
        data = file_object.read()
        file_object.close()
        return data
    except Exception as e:
        print(e)
        return ""


if __name__ == "__main__":
    try:
        continue_migration = True
        profile["src"] = load_from_disk("src_profile")
        profile["src"] = get_profile("src")
        save_2disk("src_profile", profile["src"])
        check_profile(profile["src"])

        profile["dst"] = load_from_disk("dst_profile")
        profile["dst"] = get_profile("dst")
        save_2disk("dst_profile", profile["dst"])
        check_profile(profile["dst"])
        while continue_migration:
            print("Select the [source] table:")
            src_table = select_dynamo_table(profile["src"])
            print("Select the [destination] table:")
            dst_table = select_dynamo_table(profile["dst"])

            if confirm(
                f"Start data copy\n From [{src_table}] table using [{profile['src']}] profile\n to   [{dst_table}] table using [{profile['dst']}] profile ?"
            ):
                print()
                print("Starting data copy")
                execute_migration(profile["src"], profile["dst"], src_table, dst_table)
            continue_migration = confirm("Do you want copy data from another table?")

    except Exception as e:
        print(e)
