const fileInput = document.querySelector("[type=file]");
fileInput?.addEventListener("change", function() {
  if (fileInput.files.length > 0) {
    uploadFile(fileInput.files[0]);
  }
});

const formInput = document.querySelector(".form-input");
formInput?.addEventListener("keyup", function(event) {
	if (event.key === "Enter") {
		handleUserQuery()
	}
})

function toggleSpinner(){
	const spinner = document.querySelector(".spinner");
	spinner.style.display = spinner.style.display === "block" ? "none" : "block";
}

function uploadFile(file) {
	const formData = new FormData();

	formData.append("file", file);

	toggleSpinner()
	fetch("upload", {method:"POST", body:formData})
	.then(response => {
		return response.text();
	})
	.then(upload_id => {
		window.location.href = "chat/" + upload_id;
	});
}


function handleUpload() {
	fileInput.click();
}


function handleUserQuery (){
	const url = window.location.href;
	const parts = url.split("/");
	const uploadID = parts[parts.length - 1];

	const formInput = document.querySelector(".form-input")

	const query = formInput.value;
	if (query === "") return;
	formInput.value = "";

	addElement(query, "user");

	const formData = new FormData();

	formData.append("query", query);

	toggleSpinner();
	fetch("/ask/" + uploadID, {method:"POST", body:formData})
	.then(response => response.text())
	.then(response => {
		addElement(response, "model");
		const chatContainer = document.querySelector(".chat-container");
		chatContainer.scrollTop = chatContainer.scrollHeight;
	})
	.finally(toggleSpinner);
}

function addElement(text, speaker){
	const newDiv = document.createElement("div");
	newDiv.classList.add("user-query");

	const speakerDiv = document.createElement("div");
	speakerDiv.textContent = speaker === "user" ? "You":"ChatGPT"
	const textDiv = document.createElement("div");
	textDiv.textContent = text;

	newDiv.appendChild(speakerDiv);
	newDiv.appendChild(textDiv);

	const container = document.querySelector(".chat-container2");
	container.appendChild(newDiv);
}
