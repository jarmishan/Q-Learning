import numpy

class Agent:
    def __init__(self, rewards_table, start, end):
        self.start = start
        self.end = end
        self.rewards_table = rewards_table
        
        self.SIZE = len(self.rewards_table)
        self.EPOCHS = self.SIZE * 1000
        self.EPSILON = 0.65
        self.DISCOUNT_FACTOR = 0.9
        self.LEARNING_RATE = 0.9

        self.actions = ["up", "right", "down", "left"]
        self.Q_table = numpy.zeros((self.SIZE, self.SIZE , 4))
        self.paths = []
       

    def is_terminal(self, row, column):
        if self.rewards_table[row, column] == -1:
            return False
        else: 
            return True
        
        
    def get_start(self):
        row, column = numpy.random.randint(self.SIZE), numpy.random.randint(self.SIZE)

        while self.is_terminal(row, column):
            row, column = numpy.random.randint(self.SIZE), numpy.random.randint(self.SIZE)
        return row, column
    
  
    def get_action(self, row, column, epsilon):
        if numpy.random.random() < epsilon:
            return numpy.argmax(self.Q_table[row, column])
        else:
            return numpy.random.randint(4)


    def get_next_location(self, row, column, action):
        new_row, new_column = row, column

        if self.actions[action] == "up" and row > 0:
            new_row -= 1
            
        elif self.actions[action] == "right" and column > 0:
            new_column -= 1

        elif self.actions[action] == "left" and column < self.SIZE - 1:
            new_column += 1

        elif self.actions[action] == "down" and row < self.SIZE - 1:
            new_row += 1

        return new_row, new_column


    def get_path(self, pos):
        if self.is_terminal(pos[0], pos[1]):
            path = []
        else:
            row, column = pos
            path = [(row, column)]

            while not self.is_terminal(row, column):
                action = self.get_action(row, column, 100000)
                row, column = self.get_next_location(row, column, action)
                if (row, column) in path:
                    return []
                
                path.append((row, column))
               
        return path
    

    def train(self):
        for episode in range(self.EPOCHS):
            row, column = self.get_start()
            training_path = []
            while not self.is_terminal(row, column):
                action = self.get_action(row, column, self.EPSILON)

                training_path.append((row, column))

                prev_row, prev_column = row, column
                row, column = self.get_next_location(row, column, action)

                reward = self.rewards_table[row, column]
                prev_Q = self.Q_table[prev_row, prev_column, action]
                temporal_differance = reward + (self.DISCOUNT_FACTOR * numpy.max(self.Q_table[row, column])) - prev_Q

                current_Q = prev_Q + (self.LEARNING_RATE * temporal_differance)

                self.Q_table[prev_row, prev_column, action] = current_Q

            if episode % 500 == 0:
                self.paths.append(training_path)


    def get_final_path(self):
        robot_path = self.get_path(self.start)

        if robot_path:
            drop_path = self.get_path(self.end)
        else:
            return []

        if robot_path and drop_path:
            drop_path.pop()
            drop_path.reverse()
            return robot_path + drop_path
        else:
            return []