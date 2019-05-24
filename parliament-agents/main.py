from agents.parliamentarianAgent import ParliamentarianAgent
from agents.votingSystemAgent import VotingSystemAgent
from agents.europeanParliamentAgent import EuropeanParliamentAgent
from interest import InterestArea
from interest import Interest
from state import UnionState, VoterDescription
from random import randint
from statute import Statute


class Simulation:
    def __init__(self):
        self.interestsAreas = []
        self.agents = []
        self.votingSystem = None
        self.europeanParliament = None
        self.statute = None

    def setup(self, file_name_interests_areas, file_name_agents_accounts):
        simulation.__load_interests_areas_from_file(file_name_interests_areas)
        simulation.__create_european_parliament_agent()
        simulation.__create_voting_system_agent()
        simulation.__create_parliamentarian_agents_from_file(file_name_agents_accounts)

    def __load_interests_areas_from_file(self, file_name):
        self.interestsAreas = []
        with open(file_name) as f:
            content = f.readlines()
            for line in content:
                line = line.rstrip().split("@")
                self.interestsAreas.append(InterestArea(line[0], line[1], line[2]))

    def __create_parliamentarian_agents_from_file(self, file_name):
        self.agents = []
        self.agent_id_to_address = {}
        self.agent_address_to_id = {}
        with open(file_name) as f:
            content = f.readlines()
            for line in content:
                interests = {}
                # TODO Load (now random interests)
                for interestArea in self.interestsAreas:
                    interests[interestArea] = Interest(interestArea.name, randint(1, 20), randint(1, 5))
                strength = randint(1, 2) # number of voters in political group
                line = line.rstrip().split(" ")
                agent = ParliamentarianAgent(line[0], line[1], "votingSystem@jabbim.pl", "EuropeanParliamentAgent@jabbim.pl", interests, strength)
                future = agent.start()
                agent.web.start(hostname="127.0.0.1", port=str(10000 + agent.id))
                agent.receive_message_behaviour()
                self.agents.append(agent)
                self.agent_address_to_id[line[0].casefold()] = agent.id
                self.agent_id_to_address[agent.id] = line[0].casefold() 
                self.votingSystem.voters[line[0].casefold()] = VoterDescription(agent.jid, strength)
                self.europeanParliament.parliamentarianAgentsJIDs.append(agent.jid)
                future.result()
        for agent in self.agents:
            agent.voters = {}
            for name, voter in self.votingSystem.voters.items():
                agent.voters_id_to_address = self.agent_id_to_address
                agent.voters_address_to_id = self.agent_address_to_id
                agent.voters[self.agent_address_to_id[name]] = VoterDescription(voter.jid, voter.strength)

    def __create_european_parliament_agent(self):
        # TODO Load (now random state)
        state = {}
        for interestArea in self.interestsAreas:
            state[interestArea] = randint(1, 20)
        self.europeanParliament = EuropeanParliamentAgent("EuropeanParliamentAgent@jabbim.pl", "parlAGH123",
                                                          "votingSystem@jabbim.pl", UnionState(state))
        self.europeanParliament.web.start(hostname="127.0.0.1", port="30000")
        future = self.europeanParliament.start()
        self.europeanParliament.receive_message_behaviour()
        future.result()

    def __create_voting_system_agent(self):
        self.votingSystem = VotingSystemAgent("votingSystem@jabbim.pl", "parlAGH123",
                                              "EuropeanParliamentAgent@jabbim.pl")
        self.votingSystem.web.start(hostname="127.0.0.1", port="20000")
        future = self.votingSystem.start()
        self.votingSystem.receive_message_behaviour()
        future.result()

    def start_voting(self, file_name_statute):
        # TODO Load or set (now random statute)
        statute_interests = {}
        for interestArea in self.interestsAreas:
            statute_interests[interestArea] = Interest(interestArea.name, randint(1, 20), randint(1, 5))
        self.votingSystem.set_current_statute(Statute(statute_interests))
        self.votingSystem.generate_start_voting()


if __name__ == '__main__':
    simulation = Simulation()
    simulation.setup("InterestAreas.txt", "ParliamentarianAgentAccounts.txt")
    simulation.start_voting(None)

