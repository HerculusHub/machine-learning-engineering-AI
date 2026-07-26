from mobile_ai_system.agents.supervisor_agent import SupervisorAgent


def test_name():

    agent = SupervisorAgent()

    assert agent.name == "Supervisor"


def test_run():

    state = {"task": "Analyze Verizon"}

    agent = SupervisorAgent()

    assert agent.run(state) == state