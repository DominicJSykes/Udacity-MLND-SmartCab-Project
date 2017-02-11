import random
import time
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state 
#        = None, next_waypoint = None, and a default color
        self.color = 'yellow'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to 
#        get next_waypoint
        # TODO: Initialize any additional variables here
        self.q_table = {}
        self.learning_rate = 1.0
        self.discount_rate = 0.1
        self.iteration = 0
        self.suboptimal_score_last_ten = 0
        self.reward = 0
        self.count = 0
        self.q_initialisation = 1.0

    def reset(self, destination=None):
        self.count = self.count + 1
        self.planner.route_to(destination)
        self.learning_rate = 1 / self.count**0.9
            
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, 
#        also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        if self.iteration > 0:
            self.state_new = str(self.next_waypoint) + str(inputs['light']) + str(inputs['oncoming']) + str(inputs['left']) 
            q = -100
            for i in range(len(Environment.valid_actions)):
                try:
                    if (self.q_table[self.state_new +  str(Environment.valid_actions[i])] > q):
                        q = self.q_table[self.state_new +  str(Environment.valid_actions[i])]
                        max_action = Environment.valid_actions[i]
                except KeyError:
                    if i == 3 and q == -100:
                        self.q_table.update({self.state_new + str(Environment.valid_actions[i]) : self.q_initialisation})
                        max_action = Environment.valid_actions[i]
            self.q_table[self.state + str(self.action)] = (1 - self.learning_rate)*self.q_table[self.state + str(self.action)] + self.learning_rate*(self.discount_rate * self.q_table[self.state_new + str(max_action)] + self.reward)
        
            if (self.reward < 0.6):
                if(self.count > 90):
                    self.suboptimal_score_last_ten = self.suboptimal_score_last_ten - (1 - self.reward)     

        # TODO: Update state
        self.state = str(self.next_waypoint) + str(inputs['light']) + str(inputs['oncoming']) + str(inputs['left'])
        
        # TODO: Select action according to your policy
        q = -100
        new = True
        for i in range(len(Environment.valid_actions)):
            try:
                if (self.q_table[self.state + str(Environment.valid_actions[i])] > q):
                    q = self.q_table[self.state +  str(Environment.valid_actions[i])]
                    if q == self.q_initialisation:
                        max_action = Environment.valid_actions[i]
                        new = False
                        break
            except KeyError:
                continue
        q = -100
        if new:
            for i in range(len(Environment.valid_actions)):
                try:
                    if (self.q_table[self.state + str(Environment.valid_actions[i])] > q):
                        q = self.q_table[self.state +  str(Environment.valid_actions[i])]
                        max_action = Environment.valid_actions[i]
                except KeyError:
                    self.q_table.update({self.state + str(Environment.valid_actions[i]) : self.q_initialisation})
                    max_action = Environment.valid_actions[i]
                    break
                
        self.action = max_action
        # Execute action and get reward
        self.reward = self.env.act(self, self.action)
        
        self.iteration = self.iteration + 1
        # TODO: Learn policy based on state, action, reward

def run():
    """Run the agent for a finite number of trials."""
    
    total_suboptimal_score = 0 
    
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    total_suboptimal_score = total_suboptimal_score + a.suboptimal_score_last_ten
    
    print "Suboptimal score for last ten runs: {}".format(total_suboptimal_score / 1.0)

if __name__ == '__main__':
    run()
