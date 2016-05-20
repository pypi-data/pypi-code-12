from tcell_agent.agent.agent_threads import TCellAgent
def just_return(self):
    return
TCellAgent.ensure_polling_thread_running = just_return
TCellAgent.ensure_metrics_pipe_thread_running = just_return
TCellAgent.ensure_fork_pipe_thread_running = just_return
TCellAgent.ensure_event_handler_thread_running = just_return
from tcell_agent.appsensor.manager import app_sensor_manager
app_sensor_manager.use_threads = False


from tcell_agent.config import configuration
configuration.WARN_TO_CONSOLE = False