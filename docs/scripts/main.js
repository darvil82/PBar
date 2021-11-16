const WIKI_URL = "https://github.com/DarviL82/PBar/wiki/"

const PBAR_INFO = {	// Define the wiki pages, and their corresponding tooltip
	PBar: ["PBar", "The main progress bar object, which will let us manage and customize the progress bars however we want."],
		draw: ["PBar#methods", "Draws the progress bar on the screen."],
		step: ["PBar#methods", "Add <span class='pre'>steps</span> to the first value in prange, then draw the bar."],
		text: ["PBar#text", "Text to be displayed on the progress bar."],
		conditions: ["PBar#conditions", "One or more conditions to check before each time the bar draws. If one succeeds, the specified customization sets will be applied to the bar."],

	Cond: ["Cond", "Applies different customization sets to a bar if the condition supplied succeeds."],
	animate: ["animate-function", "Animates the given PBar object by filling it by the range given, with a delay."],
	taskWrapper: ["taskWrapper-function-decorator", "Automatically changes the prange of the progress bar depending on the number of function calls inside the decorated function.<br>This will also call the <span class='pre'>PBar.step()</span> method after each function call processed."],
	ColorSet: ["PBar#colorset", "Set of colors to use when drawing the progress bar."],
	CharSet: ["PBar#charset", "Set of characters to use when drawing the progress bar."],
	FormatSet: ["PBar#formatset", "Formatting used when displaying the strings in different places around the bar."],
	barHelper: ["barHelper", "Draw a bar helper on screen indefinitely until the user exits. Returns the position of the bar helper."]
}


function addTooltip(element, content) {
	let tooltip = document.createElement("div")

	tooltip.style.borderColor = getComputedStyle(element).getPropertyValue("color")
	tooltip.className = "tooltip"
	tooltip.innerHTML = content
	element.appendChild(tooltip)
	element.style.position = "relative"	// make sure the tooltip is positioned relative to the element
}




function addLink(element, url, target="_blank") {
	element.style.cursor = "pointer"
	element.classList.add("special")
	element.addEventListener("click", () => {
		open(url, target)
	})
}



function addCodeLinks() {
	let spans = document.querySelectorAll("code span")	// get all the spans inside codes */

	for (let i = 0; i < spans.length; i++) {
		const span = spans[i]
		if (span.innerHTML in PBAR_INFO) {
			/* if the content of the element
			matches a key of wiki_pages, add a link to it with the value of
			the object */
			addLink(span, WIKI_URL+PBAR_INFO[span.innerHTML][0])
			addTooltip(span, PBAR_INFO[span.innerHTML][1])
		}
	}
}



addCodeLinks()