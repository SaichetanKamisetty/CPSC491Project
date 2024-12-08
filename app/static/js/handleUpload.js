function handleUploads(directory)
{
    const instruc = document.getElementById('instructions');
    const imageContainer = document.getElementById('image-container');
    const downloadButton = document.getElementById('download-button');
    const deleteButton = document.getElementById('delete-button');
    const formData = new FormData();

    console.log(directory.length);

    if (directory.length > 0)
    {
        for(let i = 0; i<directory.length; i++)
        {
            formData.append('files[]', directory[i]);
        }

        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data=>{
            instruc.style.display = 'none';

            imageContainer.classList.remove('hidden');
            imageContainer.innerHTML = '';

            data.files_urls.forEach(elem => {
                const imgDiv = document.createElement('div');
                imgDiv.className = 'relative';

                imgDiv.innerHTML = `
                <img src="${elem}" alt="Manga Image" class="w-full rounded-lg">
                <button class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600 focus:outline-none" onclick="removeImage('${elem}', this)">
                    x
                </button>
                `;

                imageContainer.appendChild(imgDiv);

            });
            deleteButton.classList.remove('hidden')
            downloadButton.classList.remove('hidden')
        })
        .catch(error=> {
            console.error("Error uploading files:", error),
            showError(`ERROR | Issue uploading files: ${error.message || error}`)
        });
    }
}

function removeImage(fileUrl, button)
{
    fetch('/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({file_path: fileUrl}),
        credentials: 'include'
    })
    .then(response=>response.json())
    .then(data=> {
        if (data.success) {
            button.parentElement.remove();
        } else {
            console.error("Error deleting file:", data.message);
            showError(`ERROR | Error deleting file: ${data.message}`)
        }

        const imageContainer = document.getElementById('image-container');
        const instruc = document.getElementById('instructions');
        const downloadButton = document.getElementById('download-button');
        const deleteButton = document.getElementById('delete-button');

        if (imageContainer.children.length < 1) {
            imageContainer.classList.add('hidden');
            downloadButton.classList.add('hidden')
            deleteButton.classList.add('hidden')
            instruc.style.display = '';

            location.reload();
        }
    })
    .catch(error=> {
        console.error("Error sending delete request: ", error),
        showError(`ERROR | Error sending delete request: ${error.message || error}`)
    });
}


function showError(msg, duration = 3000) {
    const errorToast = document.getElementById("error_toast");

    errorToast.textContent = msg;
    errorToast.style.display = "block";

    setTimeout(() => {
        errorToast.textContent = "";
    }, duration);
}

function downloadImages() {
    fetch('/download', {
        method: 'GET'
    })
    .then(response => response.blob()) 
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');        
        a.href = url;                                  
        a.download = 'images.zip';                     
        document.body.appendChild(a);                 
        a.click();                                    
        document.body.removeChild(a);                 
        window.URL.revokeObjectURL(url);
    })
    .catch(error=> {
        console.error('Download failed:', error),
        showError(`ERROR | Error downloading files: ${error.message || error}`)
    });
}

function deleteAllImages() {
    fetch('/deleteImages', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {

            const imageContainer = document.getElementById('image-container');
            const elements = imageContainer.querySelectorAll('*');

            elements.forEach(element => {
                element.remove()
            });

            const instruc = document.getElementById('instructions');
            const downloadButton = document.getElementById('download-button');
            const deleteButton = document.getElementById('delete-button');

            imageContainer.classList.add('hidden')
            downloadButton.classList.add('hidden')
            deleteButton.classList.add('hidden')
            instruc.style.display = '';

            location.reload();

        }
    })
    .catch(error=> {
        console.error('Issue deleting files: ', error),
        showError(`ERROR | Issue deleting files: ${error.message || error}`)
    });
}