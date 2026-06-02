import unittest

from app.session import AgentSessionStore
from tests.test_agent import FakeTemanUmkmClient


class AgentSessionStoreTest(unittest.TestCase):
    def test_get_agent_reuses_same_agent_for_same_session(self) -> None:
        store = AgentSessionStore(
            client_factory=FakeTemanUmkmClient,
            auto_login=False,
        )

        first_agent = store.get_agent("kasir-1")
        second_agent = store.get_agent("kasir-1")

        self.assertIs(first_agent, second_agent)

    def test_get_agent_creates_different_agents_for_different_sessions(self) -> None:
        store = AgentSessionStore(
            client_factory=FakeTemanUmkmClient,
            auto_login=False,
        )

        first_agent = store.get_agent("kasir-1")
        second_agent = store.get_agent("kasir-2")

        self.assertIsNot(first_agent, second_agent)


if __name__ == "__main__":
    unittest.main()
