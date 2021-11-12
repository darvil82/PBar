const WIKI_URL = "https://github.com/DarviL82/PBar/wiki/"



function addCodeLinks() {
	function addLink(element, url, target="_blank") {
		element.style.cursor = "pointer"
		element.classList.add("special")
		element.addEventListener("click", () => {
			open(url, target)
		})
	}

	const wiki_pages = {	// Define the wiki pages available
		PBar: "PBar",
		Cond: "Cond",
		animate: "animate-function",
		taskWrapper: "taskWrapper-function-decorator",
		ColorSet: "PBar#colorset",
		CharSet: "PBar#charset",
		FormatSet: "PBar#formatset",
		barHelper: "barHelper",
		Term: "Term"
	}

	let spans = document.querySelectorAll("code span")	// get all the spans inside codes */

	for (let i = 0; i < spans.length; i++) {
		const span = spans[i]
		if (span.innerHTML in wiki_pages) {
			/* if the content of the element
			matches a key of wiki_pages, add a link to it with the value of
			the object */
			addLink(span, WIKI_URL+wiki_pages[span.innerHTML])
		}
	}
}


addCodeLinks()