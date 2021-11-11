function addStuffToCode() {
	let spans = document.getElementsByTagName("span")

	function addLink(element, url, target="_blank") {
		element.style.cursor = "pointer"
		element.addEventListener("click", () => {
			open(url, target)
		})
	}


	for (let i = 0; i < spans.length; i++) {
		const span = spans[i]
		switch (span.innerHTML) {
			case "PBar":
				addLink(span, "https://github.com/DarviL82/PBar/wiki/PBar")
				break
			case "Cond":
				addLink(span, "https://github.com/DarviL82/PBar/wiki/Cond")
				break
			case "animate":
				addLink(span, "https://github.com/DarviL82/PBar/wiki/animate-function")
				break
			case "taskWrapper":
				addLink(span, "https://github.com/DarviL82/PBar/wiki/taskWrapper-function-decorator")
				break
		}
	}
}



addStuffToCode()