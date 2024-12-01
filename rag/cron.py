import threading

from crontab import CronTab
from dotenv import load_dotenv
from fastapi import FastAPI

from config.logging import Logger
from config.utils import setup_env, get_env_value


def run_cron():
    """
    Run LLM calls in set interval with cron
    """
    logger = Logger.setup_logger("rag")

    logger.info(f' [*] Healthcheck running on port 8000.')

    # instantiate cron, automatically run `cron.write()` on exit
    with CronTab(user=True) as cron:
        # clear existing cron jobs
        cron.remove_all()
        # create new job
        job = cron.new(command='python main.py')
        # set job to run at 12PM daily
        job.setall(get_env_value("CRON_SLICES"))

    # validate job
    for job in cron:
        logger.info(f"Cron job instantiated: {job}")


load_dotenv()

# run healthcheck server
app = FastAPI()

@app.get("/ping")
async def healthcheck():
    return { "status": "healthy" }

t_cron = threading.Thread(
    target=run_cron,
    daemon=True
)
t_cron.start() 
