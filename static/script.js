const dropArea = document.querySelector(".drag-area"),
  dragText = dropArea.querySelector("header"),
  button = dropArea.querySelector("button"),
  input = dropArea.querySelector("input"),
  submitButton = document.getElementById("submit-button");

let audioFile, excelFile;

button.onclick = () => {
  input.click();
};

submitButton.onclick = async () => {
  if (audioFile && excelFile) {
    const formData = new FormData();
    formData.append("excel_csv_file", excelFile);
    formData.append("audio_file", audioFile);

    try {
      const response = await fetch("/", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log(result);
    } catch (error) {
      console.error("Error submitting POST request:", error);
    }
  } else {
    alert("Please upload both an audio file and an Excel file.");
  }
};


input.addEventListener("change", function () {
  const files = this.files;
  if (files.length > 2) {
    alert("Please select only up to 2 files.");
    return;
  }

  audioFile = null;
  excelFile = null;

  for (const file of files) {
    if (file.type.startsWith("audio/")) {
      audioFile = file;
    } else if (
      file.type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
      file.type === "text/csv"
    ) {
      excelFile = file;
    }
  }

  dropArea.classList.add("active");
  showFiles(); // calling the function to show selected files
});

dropArea.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropArea.classList.add("active");
  dragText.textContent = "Release to Upload Files";
});

dropArea.addEventListener("dragleave", () => {
  dropArea.classList.remove("active");
  dragText.textContent = "Drag & Drop to Upload Files";
});

dropArea.addEventListener("drop", (event) => {
  event.preventDefault();

  const files = event.dataTransfer.files;
  if (files.length > 2) {
    alert("Please drop only up to 2 files.");
    return;
  }

  audioFile = null;
  excelFile = null;

  for (const file of files) {
    if (file.type.startsWith("audio/")) {
      audioFile = file;
    } else if (
      file.type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
      file.type === "text/csv"
    ) {
      excelFile = file;
    }
  }

  showFiles(); // calling the function to show selected files
});

function showFiles() {
  dropArea.innerHTML = ""; // Clear previous content

  if (audioFile) {
    dropArea.innerHTML += `<div class="file">${audioFile.name} (Audio)</div>`;
  }
  if (excelFile) {
    dropArea.innerHTML += `<div class="file">${excelFile.name} (Excel)</div>`;
  }

  if (!audioFile || !excelFile) {
    dropArea.innerHTML += `<div class="file">Incomplete or invalid selection</div>`;
  }

  dropArea.classList.remove("active");
  dragText.textContent = "Drag & Drop to Upload Files";
}
