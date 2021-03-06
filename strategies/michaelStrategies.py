from random import randint

class RandomWalk:
    #This class has a 50% chance to hit, and folds for best available card
    #No initialization needed since this strategy needs no initial argument
    
    def play(self, info):
        #get best fold as tuple (playerIndex, card)
        best = info.bestFold(self.player)

        #establish strategy
        x = randint(1,100)
        if x <= 50:
            return "Hit"
        else:
            return best

class OverThinker:
    '''Attempts to use basic heuristics to make decisions. Uses an additive set of assumptions for other players'
       odds of losing, then attempts to "survive" based on that set of information.
       THIS STRATEGY IS AGNOSTIC TO DECK STATE (No attempt to card count performed)'''
    #No initialization needed since this strategy needs no initial argument

    def play(self, info):
        #get best fold as tuple (playerIndex, card)
        best = info.bestFold(self.player)

        #get maximum score possible
        YouLose = max(int(60/info.noPlayers) + 1, 11)
    
        #establish board state and make assumptions
        PFolds = []
        PLoses = []
        States = []
        for player in info.players:
            if player.index == self.player.index:
                continue # this is me!
            score = player.getScore()
            stack = player.stack

            PFold = 0
            PLose = 0
            #Stack-based assumptions:
            if 10 in stack:
                PFold += 50
            if 9 in stack:
                PFold += 40
            if 8 in stack:
                PFold += 30
            if 7 in stack:
                PFold += 20

            #Score-based assumptions:    
            if score >= YouLose - 1:
                PFold += 0
                PLose += 90
            elif score >= YouLose - 2:
                PFold += 10
                PLose += 80
            elif score >= YouLose - 3:
                PFold += 20
                PLose += 70
            elif score >= YouLose - 4:
                PFold += 30
                PLose += 60
            elif score >= YouLose - 5:
                PFold += 40
                PLose += 50
            else:
                PFold += 50
                PLose += 0

            #Obviously, this will go over 100 for large stacks, mimicking real life--if a player has a 9 and a 10, she's going to fold
            PFold = min(PFold, 100)
            PLose = min(PLose, 100)
            State = (PFold, PLose)

            States.append(State)
            
            
        
        # make a decision based on current score/stack state and other players PLose/PFold
        if max(States[1]) >= 70 and YouLose - self.player.getScore() > best[1] :
            return best

        if self.player.getScore() <= YouLose - 8 and best[1] <= 3 :
            return best
        elif self.player.getScore() >= YouLose - 4 and best[1] <= 2 :
            return best
        elif self.player.getScore() >= YouLose - 2 and best[1] <= 1 :
            return best
        else :
            return "Hit"


class OverThinkerJrTHEDESTROYER:
    #THIS BOT IS GONNA LOSE HARD, Y'ALL, I WROTE IT POORLY IN LIKE FIFTEEN MINUTES
    def __init__(self):
        from collections import Counter
        self.Counter = Counter
        


    def play(self, info):
        #get best fold as tuple (playerIndex, card)
        best      = info.bestFold(self.player)
        c = self.Counter(info.deck) #Allows card counting. Lame.
        
        
        #get score information
        highscore = max(p.getScore() for p in info.players)
        myscore   = self.player.getScore()

        #get board state
        StackSums = [sum(p.stack) for p in info.players]
        StackList = []
        for p in info.players:
            StackList.extend(p.stack) #making StackList a list of numbers, not a list of lists        
        Scores    = [p.getScore() for p in info.players]
        NumTens   = StackList.count(10)
        NumNines  = StackList.count(9)
        NumEights = StackList.count(8)

        

        #establish strategy

        if max(self.player.stack) <= 4:
            return "Hit" #It's fine.

        if max(StackSums) >= 17 and sum(self.player.stack) < 17:
            return "Hit" #trying to implement a risk-seeking strategy that hopes others fold or lose
            

            if sum(self.player.stack) > 17:
                if c[10] >= 5 and self.player.stack.count(10) == 0:
                    return "Hit" #gulp
                elif c[9] >= 5 and self.player.stack.count(9) == 0:
                    return "Hit" #gulp
                elif c[8] >= 4 and self.player.stack.count(8) == 0:
                    return "Hit" #gulp
                else:
                    return best                
            else:
                return "Hit"
           
            
        
