import os
from dotenv import load_dotenv

load_dotenv()
# no default, must be set...
mediator_invitation_url = os.environ["MEDIATOR_INVITATION_URL"]

# we can add defaults for local development
database = os.getenv("DATABASE", "locustfile.db")

step_time = int(os.getenv("STEP_TIME", 30))
step_load = int(os.getenv("STEP_LOAD", 10))
time_limit = int(os.getenv("TIME_LIMIT", 300))
spawn_rate = float(os.getenv("SPAWN_RATE", 10))


def print_config():
    print("configuration\n--------------------")
    print(f"mediator_invitation_url = {mediator_invitation_url}")
    print(f"database = {database}")
    print(f"step_time = {step_time}")
    print(f"step_load = {step_load}")
    print(f"time_limit = {time_limit}")
    print(f"spawn_rate = {spawn_rate}\n")