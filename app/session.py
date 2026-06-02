from __future__ import annotations

from collections.abc import Callable

from .agent import TemanUmkmAgent
from .api import TemanUmkmClient


ClientFactory = Callable[[], TemanUmkmClient]


class AgentSessionStore:
    def __init__(
        self,
        client_factory: ClientFactory = TemanUmkmClient,
        auto_login: bool = True,
    ) -> None:
        self.client_factory = client_factory
        self.auto_login = auto_login
        self.sessions: dict[str, TemanUmkmAgent] = {}

    def get_agent(self, session_id: str) -> TemanUmkmAgent:
        if session_id not in self.sessions:
            self.sessions[session_id] = self._create_agent()

        return self.sessions[session_id]

    def _create_agent(self) -> TemanUmkmAgent:
        client = self.client_factory()
        agent = TemanUmkmAgent(client)

        if self.auto_login:
            agent.login()

        return agent
