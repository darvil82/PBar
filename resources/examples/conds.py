import pbar

myConditions = (
	pbar.Cond("percentage >= 50", colorset=pbar.ColorSet.YELLOW, charset=pbar.CharSet.BRICKS),
	pbar.Cond("percentage == 100", colorset=pbar.ColorSet.GREEN),
	pbar.Cond("text <- error", colorset=pbar.ColorSet.RED, formatset=pbar.FormatSet.DESCRIPTIVE)
)

mybar = pbar.PBar(conditions=myConditions)

try:
	pbar.animate(mybar, range(50))
except KeyboardInterrupt:
	mybar.text = "Error!"
	mybar.draw()