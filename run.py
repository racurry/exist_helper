from lib import SecretsManager, Exist, Things3
import sys
from datetime import date, timedelta

class ExistHelper():

    def run(self):
        secrets_manager = SecretsManager()
        exist_client_id = secrets_manager.get('exist_client_id')
        exist_client_secret = secrets_manager.get('exist_client_secret')

        if not exist_client_id or not exist_client_secret:
            print("You need to create an exist client, and get an ID and Secret")
            print("Visit https://exist.io/account/apps/ and create an app")
            print("===================")
            exist_client_id = input("Exist client id: ")
            secrets_manager.set('exist_client_id', exist_client_id)
            exist_client_secret = input("Exist client secret: ")
            secrets_manager.set('exist_client_secret', exist_client_secret)

        exist_access_token = secrets_manager.get('exist_access_token')
        if not exist_access_token:
            tokens = Exist.get_oauth_tokens(client_secret=exist_client_secret, client_id=exist_client_id)
            secrets_manager.set('exist_access_token', tokens.get('access_token'))
            secrets_manager.set('exist_refresh_token', tokens.get('refresh_token'))

        # refresh our tokens if requested
        if "--r" in sys.argv:
            # Exchanging refresh tokens
            exist_refresh_token = secrets_manager.get('exist_refresh_token')
            tokens = Exist.exchange_refresh_token(
                client_secret=exist_client_secret, 
                client_id=exist_client_id, 
                refresh_token=exist_refresh_token
            )
            print(f"Refresh token has been exchanged for a new one")
            secrets_manager.set('exist_access_token', tokens.get('access_token'))
            secrets_manager.set('exist_refresh_token', tokens.get('refresh_token'))

        exist_access_token = secrets_manager.get('exist_access_token')
        exist = Exist(access_token=exist_access_token)

        if "--a"in sys.argv:
            exist.acquire_attribute('tasks_completed')

        print("Getting current values from Exist:")
        print("===============")
        exist.get_values()

        things3 = Things3()
        print("Updating new values from Things")

        today = date.today()
        yesterday = today - timedelta(days=1)
        todays_task_count = things3.count_of_completed_tasks_for_date(today)
        yesterdays_task_count = things3.count_of_completed_tasks_for_date(yesterday)

        exist.set_value(attribute='tasks_completed', value=todays_task_count, date=today)
        exist.set_value(attribute='tasks_completed', value=yesterdays_task_count, date=yesterday)
        

        print("Getting current values from Exist:")
        print("===============")
        exist.get_values()

ExistHelper().run()