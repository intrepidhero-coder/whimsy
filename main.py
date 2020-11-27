import os
import json
from random import choice, randint

GLOBALS = {"randint": randint, "choice": choice}

def processDescription(desc, world):
    if "condition" in desc:
        if eval(desc["condition"], GLOBALS, world):
            print(desc["description"])
    else:
        print(desc)


def processFlag(option, world):
    if "message" in option:
        print(option["message"])
        choice = input("Press any key")
    if "flag" in option:
        world[option["flag"]] = True
    if "increment" in option:
        world[option["increment"]] += 1
    if "eval" in option:
        options["eval"]["flag"] = eval(option["eval"]["exp"], GLOBALS, world)


def processDestinations(destinations, world):
    if eval(destinations["if"], GLOBALS, world):
        return destinations["then"]
    else:
        return destinations["else"]


def main():
    world = None
    currentNodeKey = "BEGIN"
    if os.path.exists("usergame.json"):
        choice = input("Do you want to load the saved game? Y/N ").lower().strip()
        if len(choice) > 0 and choice[0] == "y":
            world = json.load(open("usergame.json"))
            currentNodeKey = world["CURRENT"]
    if not world:
        world = json.load(open("world.json"))

    world["MOVES"] = 0
    while currentNodeKey != "END":
        currentNode = world[currentNodeKey]
        if not "visited" in currentNode:
            # visited is not in the base world file
            currentNode["visited"] = False
        for key in ("predescription", "description", "postdescription"):
            if key in currentNode:
                processDescription(currentNode[key], world)
            print()
        if not "options" in currentNode:
            # handle description only nodes
            choice = input("Press any key")
            currentNodeKey = currentNode["destination"]
            # optionally, these nodes can affect game state
            processFlag(currentNode, world)
            continue
        else:
            # display options
            options = [opt for opt in currentNode["options"] if not "condition" in opt or eval(opt["condition"], GLOBALS, world)]
            for n, opt in enumerate(options):
                print("{}. {}".format(n, opt["label"]))
        print("(save or quit)")
        choice = input("? ").lower().strip()
        # basic game commands
        if "save".startswith(choice):
            world["CURRENT"] = currentNodeKey
            open("usergame.json", "w").write(json.dumps(world))
        elif "quit".startswith(choice):
            choice = input("Are you sure you want to quit? Y/N ").lower().strip()
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
                    currentNodeKey = processDestinations(option["destinations"], world)
                else:
                    currentNodeKey = option["destination"]
                    # or, choosing the option can affect the game state (flags)
                    processFlag(option, world)
                # last thing before leaving a node: mark it visited and record a move
                currentNode["visited"] = True
                world["MOVES"] += 1
    # TODO: display acheivments


if __name__ == "__main__":
    main()
