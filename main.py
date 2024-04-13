import json
import os
import zipfile

followers_path = 'connections/followers_and_following/followers_1.json'
following_path = 'connections/followers_and_following/following.json'
whitelist_file = 'whitelist.txt'
data_dir = 'instagram_data'


def extract_files():
    """
    Extracts the followers and following JSON files from the Instagram data archive.
    """
    success = False
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_contents = zip_ref.namelist()
                    for path_to_extract in [followers_path, following_path]:
                        if path_to_extract in zip_contents:
                            # Extract the specific file
                            zip_ref.extract(path_to_extract, path=root)
                            print(f'Extracted {path_to_extract} from {zip_path} to {root}')
                            success = True

    if not success:
        raise FileNotFoundError("Instagram data archive not found. Please download the archive from Instagram.")


def get_followers():
    """
    Extracts the list of followers of the account.
    """
    users = []
    with open(os.path.join(data_dir, followers_path), 'r') as file:
        data = json.load(file)
        if data and isinstance(data, list):
            for instance in data:
                for item in instance["string_list_data"]:
                    # print("Value:", item["value"])
                    # print("Href:", item["href"])
                    # print("Timestamp:", item["timestamp"])
                    users.append(item["value"])

    return users


def get_following():
    """
    Extracts the list of users that the account is following.
    """
    users = []
    with open(os.path.join(data_dir, following_path), 'r') as file:
        data = json.load(file)
        if 'relationships_following' in data:
            for entry in data['relationships_following']:
                if 'string_list_data' in entry and isinstance(entry['string_list_data'], list):
                    for item in entry['string_list_data']:
                        # print("Value:", item["value"])
                        # print("Href:", item["href"])
                        # print("Timestamp:", item["timestamp"])
                        users.append(item["value"])

    return users


def get_non_followers(followers: list[str], following: list[str]):
    """
    Returns the list of users that the account is following but are not following back.
    """
    return [user for user in following if user not in followers]


def add_user_to_whitelist(user):
    with open(whitelist_file, 'a') as file:
        file.write(user + '\n')


def get_whitelist():
    try:
        with open(whitelist_file, 'r') as file:
            return file.read().splitlines()

    except FileNotFoundError:
        return []


def main():
    extract_files()

    followers = get_followers()
    following = get_following()
    non_followers = get_non_followers(followers, following)
    whitelist = get_whitelist()

    print(f"\nFollowers: {len(followers)}")
    print(f"Following: {len(following)}")
    print(f"Non-followers: {len(non_followers)}")
    print(f"Whitelist: {len(whitelist)}")

    filtered_non_followers = [user for user in non_followers if user not in whitelist]
    flagged_users = []

    for index, user in enumerate(filtered_non_followers):
        if user not in whitelist:
            print(f"\n{index + 1}/{len(filtered_non_followers)} - {user}")
            print(f"Instagram: https://www.instagram.com/{user}")
            user_input = input("Would you like to add this user to the whitelist? (y/n): ")

            if user_input.lower() == 'y':
                add_user_to_whitelist(user)
                print(f"{user} has been added to the whitelist.")
            else:
                flagged_users.append(user)
                print(f"{user} has not been added to the whitelist.")

    print("\nFlagged users:")
    for user in flagged_users:
        print(f"https://www.instagram.com/{user}")


if __name__ == "__main__":
    main()
