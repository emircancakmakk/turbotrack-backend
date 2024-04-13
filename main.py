import os
from lib.itslearning import ItsLearning
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_users_informations():
    response = supabase.table('users').select('*').execute()

    data = response.data
    if not data:
        print("No users found")
        return None

    users_informations = [(user['itslearning_username'], user['itslearning_password'], user['organisation']) for user in data]
    return users_informations

def create_users():
    users_informations = get_users_informations()
    if not users_informations:
        print("No user information found")
        return []

    itslearning_users = []
    for username, password, organisation in users_informations:
        organisation_id = ItsLearning.search_organisation(organisation)
        if not organisation_id:
            print(f"Organisation '{organisation}' not found")
            continue

        try:
            itslearning_user = ItsLearning.fetch_organisation(organisation_id[0]['id']).authenticate(username, password)
            itslearning_user.fetch_info()
            itslearning_users.append(itslearning_user)
        except Exception as e:
            print(f"Error creating user for '{username}': {e}")

    return itslearning_users


def add_tasks():
    itslearning_users = create_users()

    for itslearning_user in itslearning_users:
        user_id = itslearning_user.id
        user_tasks = []

        for task in itslearning_user.tasks:
            user_task_t = (task['id'], task['name'], task['courseName'], task['deadline'])
            user_tasks.append(user_task_t)

        for task_id, task_name, task_course_name, task_deadline in user_tasks:
            existing_task = supabase.table('tasks').select('*').eq('task_id', task_id).eq('user_id', user_id).execute()

            if existing_task.data:
                print(f"Task '{task_name}' for user '{user_id}' already exists in the database.")
                continue

            new_task = {
                'task_id': task_id,
                'user_id': user_id,
                'name': task_name,
                'course': task_course_name,
                'deadline': task_deadline
            }

            insert_response = supabase.table('tasks').insert(new_task).execute()