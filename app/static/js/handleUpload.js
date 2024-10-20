function handleUploads(directory)
{
    const instruc = document.getElementById('instructions');
    const imageContainer = document.getElementById('image-container');
    const formData = new FormData();

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
        })
        .catch(error=>console.error("Error uploading files:", error));
    }
}

function removeImage(fileUrl, button)
{
    fetch('/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({file_path: fileUrl})
    })
    .then(response=>response.json())
    .then(data=> {
        if (data.success) {
            button.parentElement.remove();
        } else {
            console.error("Error deleting file:", data.message);
        }

        const imageContainer = document.getElementById('image-container');
        const instruc = document.getElementById('instructions');
        if (imageContainer.children.length < 1) {
            imageContainer.classList.add('hidden');
            instruc.style.display = 'initial';
        }
    })
    .catch(error => console.error('Error sending delete request: ', error))
}