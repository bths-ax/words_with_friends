# words with friends

for project 4 of my digital electronics class, we were told to create a state machine that would
display and cycle between 2 words on a seven segment display depending on the state of an external
variable. but this also meant that we would need to do simplify 10 different boolean expressions
by hand through k-mapping, and then build the circuit ourselves later too. and that's like a lot
of work

## the solution

so i made a solver to programmatically find which 2 words would result in the simplest boolean
expressions for the sake of my poor innocent hands :D

## how were the results?

i feel like this was more work than just choosing 2 random words and building it...

## credits so the school doesnt sue me or smth

- word list from [this guy on github](https://github.com/dolph/dictionary)
- quine-mccluskey algorithm from [wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- i was gonna use petrick's method for the prime implicant simplification but i got lazy (but [here
  it is](https://en.wikipedia.org/wiki/Petrick%27s_method) anyways)
