import os
import json
from random import choice, randint


class AdventureGame:
    GLOBALS = {"randint": randint, "choice": choice}

    def __init__(self):
        self.world = None
        self.main()

    def output(self, message=""):
        print(message)

    def input(self, prompt=""):
        return input(prompt)

    def eval(self, c):
        return eval(c, self.GLOBALS, self.world)

    def processDescription(self, desc):
        if "condition" in desc:
            if self.eval(desc["condition"]):
                self.output(desc["description"])
        else:
            self.output(desc)

    def processFlag(self, option):
        if "message" in option:
            self.output(option["message"])
            choice = self.input("Press any key")
        if "flag" in option:
            self.world[option["flag"]] = True
        if "increment" in option:
            self.world[option["increment"]] += 1
        if "eval" in option:
            options["eval"]["flag"] = self.eval(option["eval"]["exp"])

    def processDestinations(self, destinations):
        if self.eval(destinations["if"]):
            return destinations["then"]
        else:
            return destinations["else"]

    def main(self):
        currentNodeKey = "BEGIN"
        if os.path.exists("usergame.json"):
            choice = (
                self.input("Do you want to load the saved game? Y/N ").lower().strip()
            )
            if len(choice) > 0 and choice[0] == "y":
                self.world = json.load(open("usergame.json"))
                currentNodeKey = self.world["CURRENT"]
        if not self.world:
            self.world = json.load(open("world.json"))

        self.world["MOVES"] = 0
        while currentNodeKey != "END":
            currentNode = self.world[currentNodeKey]
            if not "visited" in currentNode:
                # visited is not in the base self.world file
                currentNode["visited"] = False
            for key in ("predescription", "description", "postdescription"):
                if key in currentNode:
                    self.processDescription(currentNode[key])
                self.output()
            if not "options" in currentNode:
                # handle description only nodes
                choice = self.input("Press any key")
                currentNodeKey = currentNode["destination"]
                # optionally, these nodes can affect game state
                self.processFlag(currentNode)
                continue
            else:
                # display options
                options = [
                    opt
                    for opt in currentNode["options"]
                    if not "condition" in opt or self.eval(opt["condition"])
                ]
                for n, opt in enumerate(options):
                    self.output("{}. {}".format(n, opt["label"]))
            self.output("(save or quit)")
            choice = input("? ").lower().strip()
            # basic game commands
            if "save".startswith(choice):
                self.world["CURRENT"] = currentNodeKey
                open("usergame.json", "w").write(json.dumps(self.world))
            elif "quit".startswith(choice):
                choice = (
                    self.input("Are you sure you want to quit? Y/N ").lower().strip()
                )
                if len(choice) > 0 and choice[0] == "y":
                    return
            else:
                # did the user select a valid option?
                try:
                    choice = int(choice)
                except:
                    continue
                if choice in range(len(options)):
                    option = options[choice]
                    if "destinations" in option:
                        # an option can lead to different destinations depending on game state
                        currentNodeKey = self.processDestinations(
                            option["destinations"]
                        )
                    else:
                        currentNodeKey = option["destination"]
                        # or, choosing the option can affect the game state (flags)
                        self.processFlag(option)
                    # last thing before leaving a node: mark it visited and record a move
                    currentNode["visited"] = True
                    self.world["MOVES"] += 1
        # TODO: display acheivments


if __name__ == "__main__":
    AdventureGame()
