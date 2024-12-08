function translateManga()
{
    const gptInput = document.getElementById('chatGPT-key');
    const textSize = document.getElementById('textsize');
    const checkbox = document.getElementById('empty-textboxes');
    const formData = new FormData(); 

    const imageContainer = document.getElementById('image-container');

    if (!imageContainer.classList.contains('hidden'))
    {
        let apiKey = "";
        let textSize_ = 100;
        let checkbox_ = false;

        if (!gptInput.value)
        {
            showError(`ERROR | Input ChatGPT key`)
            return
        }
        if (textSize.value)
        {
            if (textSize.value <= 0 || textSize.value > 100)
            {
                showError(`ERROR | Input valid text size values 1-100`)
                return
            }
            textSize_ = textSize.value
        }
        apiKey = gptInput.value
        checkbox_ = checkbox.checked
        formData.append('gptInput', apiKey)
        formData.append('textSize', textSize_)
        formData.append('checkbox', checkbox_)

        
        fetch("/translate", {
            method: "POST",
            cache: 'no-cache',
            body: formData,
            credentials: 'include',
        })
        .then(response => response.json())
        .then(data=>{
            if (data.success) {
                const imageContainer = document.getElementById('image-container');
                imageContainer.innerHTML = '';

                data.fileUrls.forEach(elem => {
                    const timestamp = new Date().getTime();
                    const updatedUrl = `${elem}?t=${timestamp}`;
                    const imgDiv = document.createElement('div');
                    imgDiv.className = 'relative';

                    imgDiv.innerHTML = `
                    <img src="${updatedUrl}" alt="Manga Image" class="w-full rounded-lg">
                    <button class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600 focus:outline-none" onclick="removeImage('${elem}', this)">
                        x
                    </button>
                    `;

                    imageContainer.appendChild(imgDiv);
                });
            }
            else {
                console.log("error");
                showError(`ERROR | ${data.message}`)
            }
        })
        .catch(error=> {
            console.error("Error with sending translation request of files:", error)
            showError(`ERROR | Error with sending translation request of files: ${error.message || error}`)
        });
    } 
    else
    {
        showError("ERROR | You did not upload any images! Please upload some and try again.")
        return;
    }
}

function showError(msg, duration = 3000) {
    const errorToast = document.getElementById("error_toast");

    errorToast.textContent = msg;
    errorToast.style.display = "block";

    setTimeout(() => {
        errorToast.textContent = "";
    }, duration);
}

const eventSource = new EventSource('/translation-progress');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const translation_process = document.getElementById('translation_process');

    switch(data.status) {
        case 'waiting':
            translation_process.textContent = "[PROGRESS]: Waiting for Translation Request."
            break;
        case 'bubbles':
            translation_process.textContent = "[PROGRESS]: Detecting text bubbles for all images."
            break;
        case 'text':
            translation_process.textContent = "[PROGRESS]: Extracting text from images."
            break;
        case 'cleaning':
            translation_process.textContent = "[PROGRESS]: Cleaning text from images."
            break;
        case 'translate':
            translation_process.textContent = "[PROGRESS]: Translating text via OpenAI."
            break;
        case 'processing':
            translation_process.textContent = "[PROGRESS]: Adding text back to all images."
            break;
        case 'complete':
            translation_process.textContent = "[PROGRESS]: Translation done. Ready to download."
            break;
    }
};