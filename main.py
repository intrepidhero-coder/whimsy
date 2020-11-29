import os
import json
from random import choice, randint

ABOUT = '''
Welcome to Wandering Whimsy!
A light adventure game by FadedBlueSky Software
Copyright: Brian Davis 2020
Icon: Lighthouse by Nociconist from the Noun Project
'''

GLOBALS = {"randint": randint, "choice": choice}

world = None
outputFunc = print

def output(message):
    if world["BACKWORDS"]:
        message = "\n".join(["\u202e" + line for line in message.splitlines()])
    outputFunc(message)


def _eval(c):
    global GLOBALS
    global world
    return eval(c, GLOBALS, world)


def processDescription(desc):
    if "condition" in desc:
        if _eval(desc["condition"]):
            output(desc["description"])
    else:
        output(desc)


def processFlag(option):
    global world
    if "message" in option:
        output(option["message"])
    if "flag" in option:
        world[option["flag"]] = True
    if "increment" in option:
        world[option["increment"]] += 1
    if "eval" in option:
        world[option["eval"]["flag"]] = _eval(option["eval"]["exp"])


def processDestinations(destinations):
    if _eval(destinations["if"]):
        return destinations["then"]
    else:
        return destinations["else"]


def engine():
    global world
    currentNodeKey = "BEGIN"
    if os.path.exists("usergame.json"):
        choice = (yield "Do you want to load the saved game? Y/N ").lower().strip()
        if len(choice) > 0 and choice[0] == "y":
            world = json.load(open("usergame.json"))
            currentNodeKey = world["CURRENT"]
    if not world:
        world = json.load(open("world.json"))

    world["MOVES"] = 0
    while currentNodeKey != "END":
        currentNode = world[currentNodeKey]
        k = str(world["MOVES"])
        if k in world["EVENTS"]:
            e = world["EVENTS"][k]
            output(e["message"])
            if "jump" in e:
                choice = yield "Press Enter"
                currentNodeKey = e["jump"]
                continue
        if not "visited" in currentNode:
            # visited is not in the base world file
            currentNode["visited"] = False
        # optionally, nodes can affect game state
        processFlag(currentNode)
        for key in ("predescription", "description", "postdescription"):
            if key in currentNode:
                processDescription(currentNode[key])
            output("")
        if not "options" in currentNode:
            # handle description only nodes
            choice = yield "Press Enter"
            currentNodeKey = currentNode["destination"]
            currentNode["visited"] = True
            world["MOVES"] += 1
            continue
        else:
            # display options
            options = [
                opt
                for opt in currentNode["options"]
                if not "condition" in opt or _eval(opt["condition"])
            ]
            for n, opt in enumerate(options, 1):
                output("{}. {}".format(n, opt["label"]))
        output("(save, quit or about)")
        choice = (yield "? ")
        choice = choice.lower().strip()
        # basic game commands
        if "save".startswith(choice):
            world["CURRENT"] = currentNodeKey
            open("usergame.json", "w").write(json.dumps(world))
        elif "quit".startswith(choice):
            choice = (yield "Are you sure you want to quit? Y/N ").lower().strip()
            if len(choice) > 0 and choice[0] == "y":
                break
        elif "about".startswith(choice):
            output(ABOUT)
        else:
            # did the user select a valid option?
            try:
                choice = int(choice)
            except:
                continue
            if choice in range(1, len(options)+1):
                option = options[choice - 1]
                if "destinations" in option:
                    # an option can lead to different destinations depending on game state
                    currentNodeKey = processDestinations(option["destinations"])
                else:
                    currentNodeKey = option["destination"]
                    # or, choosing the option can affect the game state (flags)
                    processFlag(option)
                # last thing before leaving a node: mark it visited and record a move
                currentNode["visited"] = True
                world["MOVES"] += 1
    # Display achievements
    output("")
    output("Final Score: {}".format(randint(1, 10000)))
    for item in world["SCORE"]:
        if "condition" in item:
            if _eval(item["condition"]):
                output(item["message"])
        elif "value" in item:
            output(item["message"].format(_eval(item["value"])))
    choice = yield "Press Enter"

def main():
    game = engine()
    prompt = next(game)
    while True:
        try:
            prompt = game.send(input(prompt))
        except StopIteration:
            break


if __name__ == "__main__":
    main()
