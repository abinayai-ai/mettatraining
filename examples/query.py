from hyperon import MeTTa, V, E, S

metta = MeTTa()
print(metta.run("(Parent Tom Bob)"))
print(metta.run("(Parent Bob Ann)"))
print(metta.run("(Parent Ann Liz)"))

# print(metta.run("!(match &self (Parent $x Bob) $x)"))
# output = metta.run("!(match &self (Parent $x Bob) $x)") # returns as a Python list
# print(output[0][0])

# print(
#     metta.run(
#         "!(match &self (Parent $x Liz) (match &self (Parent $y $x) ($y is the grand parent of Liz)))"
#     )
# )

# with open("family.metta") as file:
#     metta.run(file.read()) # loads the metta file
#     output = metta.run("!(grandparent Liz)")
#     # print(output)
#     # metta.run("!(add-atom &self (Parent Tom Frank))")
#     metta.run("(Parent Tom Frank)")
#     metta.run("(Parent Monica John)")
#     atoms = metta.run("!(parent John)") # Tom

#     print(atoms)

## Parsing MeTTa Code
# parse_single, parse_all: add unreduced atoms to the space
# run: run a query
# print(metta.run("!(+ 1 2)"))
# print(metta.parse_single("!(+ 1 2)"))
# print(metta.parse_single("(A B)(C D)"))
# print(metta.parse_all("(A B)(C D)(E F)"))

# atom = metta.parse_single(
#     "(CourseInfo MeTTaPythonBasics ((Accessing Program Space) (Parsing MeTTa Code) (MeTTa Runner Class)))"
# )
# (CourseInfo CourseTitle (subtitles))
# metta.space().add_atom(atom)
# payload_atom = metta.run(
#     "!(match &self (CourseInfo MeTTaPythonBasics $payload) $payload)"
# )[0][0]

# print(payload_atom)

# E -> creates metta expressions
# V -> creates metta variables
# S -> creates metta symbols

# name = S("Sam")
# print(name)
# variable = V("x")
# print(variable)
# # (Parent Bob Tom)
# expr = E(S("Parent"), S( "Bob"), S("Tom"))
# print(expr)

# (Parent $x Bob)
expr_atom = E(S("Parent"), V("x"), S("Bob"))
print(expr_atom)
output = metta.space().query(expr_atom) # mattern matched output: Tom
print(output)
