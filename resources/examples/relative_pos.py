import pbar, random, string, time

pbar.Term.set_scroll_limit(3)

my_bar = pbar.PBar(
	position=("r", "r1"),
	size=(40, 1),
	text="Bit hard to read!",
	centered=False,
	contentg=pbar.ContentGens.center_x
)

for char in pbar.iter(random.choices(string.ascii_letters+"\n"*4, k=1000), my_bar):
	print(char, end="")
	time.sleep(0.01)