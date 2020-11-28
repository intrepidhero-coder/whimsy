import json
from spellchecker import SpellChecker

spell = SpellChecker()

SPELLCHECK = False

w = json.loads(open('world.json').read())
open('world.json.pp', 'w').write(json.dumps(w))

# check for 
# orphan nodes (in world but not in any destinations)
tocheck = list(w.values())
nodes_temp = [key for key in w.keys() if hasattr(w[key], "keys")]
print("You have {} nodes.".format(len(nodes_temp)))
while tocheck:
    n = tocheck.pop()
    if type(n) is str and not n.upper() == n:
        words = [word.strip("()!?.,\"'-") for word in n.split()]
        unk = spell.unknown(words)
        if unk and SPELLCHECK:
            print("Possible misspelled word: {} in {}".format(unk, n))

    if type(n) is list:
        tocheck.extend(n)
        continue
    if hasattr(n, "values"):
        tocheck.extend(list(n.values()))
        # all flags initialized
        for k in ("flag", "increment"):
            if k in n:
                if not n[k] in w:
                    print("Uninitialized flag: {}".format(n[k]))
        for k in ("destination", "then", "else"):
            if k in n:
                d = n[k]
                if d in nodes_temp:
                    nodes_temp.remove(d)
                if not d in w:
                    # missing nodes (in destinations but not world)
                    print("Invalid destination: {}".format(d))
        # consistent punctuation in options
        if "label" in n:
            l = n["label"]
            if l[-1] == '"':
                c = l[-2]
            else:
                c = l[-1]
            if not c in ".!?":
                print("Might have missing punctuation on label: {}".format(l))

if len(nodes_temp) > 0:
    print("{} Orphans: {}".format(len(nodes_temp), nodes_temp))

# spellcheck 
