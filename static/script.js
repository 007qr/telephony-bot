const dropArea = document.querySelector(".drag-area"),
  button = dropArea.querySelector("button"),
  input = dropArea.querySelector("input"),
submitButton = document.getElementById("submit-button");

let audioFile, excelFile;

button.onclick = () => {
  input.click();
};

submitButton.addEventListener('click', async (event) => {
  submitButton.classList.add('button--loading');
  
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
      submitButton.classList.remove('button--loading');  


      if (response.status === 400) {
        showSnackbar(result);
      } else {
        showSnackbar(`Upload successful!, Sending calls`);
      }


    } catch (error) {
      submitButton.classList.remove('button--loading');  
      console.error("Error submitting POST request:", error);
      showSnackbar("Upload failed. Please try again.", 5000); // Show error message
    }
  } else {
    submitButton.classList.remove('button--loading');
    showSnackbar("Please upload both an audio file and an Excel file.");
  }
});




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
}

function showSnackbar(message, duration = 3000) {
  const snackbar = document.getElementById("snackbar");
  snackbar.textContent = message;
  snackbar.classList.add("show");

  setTimeout(() => {
    snackbar.classList.remove("show");
  }, duration);
}
