import pbar, random, string, time, os

pbar.Term.set_scroll_limit(os.get_terminal_size()[1]//2)

bottom = pbar.PBar(
	position=(0, -1),
	size=(-1, 1),
	contentg=pbar.ContentGens.center_x,
	colorset=pbar.ColorSet.YELLOW,
	charset=pbar.CharSet.ROUNDED,
)

right = pbar.PBar(
	position=(-1, "c"),
	size=(2, -15),
	contentg=pbar.ContentGens.center_y,
)

top = pbar.PBar(
	position=(0, 1),
	size=(-1, 1),
	contentg=pbar.ContentGens.right,
	inverted=True,
	formatset=pbar.FormatSet.TITLE_SUBTITLE,
	charset=pbar.CharSet.DIFF,
)

rel = pbar.PBar(
	position=("r1", "r1"),
	size=(40, 9),
	text="I'm moving around!",
	colorset=pbar.ColorSet.DARVIL,
	centered=False,
	contentg=pbar.ContentGens.center,
	charset=pbar.CharSet.DOUBLE,
	formatset={
		"title": "Message: <text>",
		"subtitle": "Elapsed: <etimef>s, Remaining: <rtimef>s!"
	}
)


for char in pbar.iter(random.choices(string.ascii_letters+"\n"*2, k=1000), bottom, right, top, rel):
	print(char, end="")
	time.sleep(0.01)