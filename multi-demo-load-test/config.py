import os
from dotenv import load_dotenv

load_dotenv()
# no default, must be set...
mediator_invitation_url = os.environ["MEDIATOR_INVITATION_URL"]

# we can add defaults for local development
database = os.getenv("DATABASE", "locustfile.db")
step_time = int(os.getenv("STEP_TIME_SECS", 20))
step_load = int(os.getenv("USERS_ADDED_PER_STEP", 5))
time_limit = int(os.getenv("TIME_LIMIT_MINS", 10))
user_limit = int(os.getenv("USER_LIMIT", 30))
spawn_pct = float(os.getenv("SPAWN_PCT", 0.5))


def print_config():
    print("configuration\n--------------------")
    print(f"mediator_invitation_url = {mediator_invitation_url}")
    print(f"database = {database}")
    print(f"step_time = {step_time}")
    print(f"step_load = {step_load}")
    print(f"time_limit = {time_limit}")
    print(f"user_limit = {user_limit}")
    print(f"spawn_pct = {spawn_pct}\n")
