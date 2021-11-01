import pbar

myConditions = (
	pbar.Cond("percentage >= 50", pbar.ColorSet.YELLOW, pbar.CharSet.BRICKS),
	pbar.Cond("percentage == 100", pbar.ColorSet.GREEN),
	pbar.Cond("text <- error", pbar.ColorSet.RED, formatset=pbar.FormatSet.DESCRIPTIVE)
)

mybar = pbar.PBar(conditions=myConditions)

try:
	pbar.animate(mybar, range(50))
except KeyboardInterrupt:
	mybar.text = "Error!"
	mybar.draw()