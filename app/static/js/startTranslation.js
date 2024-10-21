function translateManga()
{
    const instruc = document.getElementById('instructions');
    const gptInput = document.getElementById('chatGPT-key');
    const textSize = document.getElementById('textsize');

    const imageContainer = document.getElementById('image-container');

    if (!imageContainer.classList.contains('hidden'))
    {
        fetch("/translate", {
            method: "POST",
            cache: 'no-cache'
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
            }
        })
        .catch(error=>console.error("Error with translation of files:", error));
    } 
    else
    {
        return;
    }
}