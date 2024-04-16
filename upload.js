document.getElementById('uploadForm').onsubmit = async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = async function(event) {
            const imageBase64 = event.target.result.split(',')[1]; // Remove the "data:image/*;base64," part
            const imageId = "unique_image_id_" + new Date().getTime(); // Generate a unique ID based on timestamp

            const payload = {
                id: imageId,
                image: imageBase64
            };

            // Send the base64 image to the Flask server
            const response = await fetch('http://localhost:5001/upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const responseJson = await response.json();
            document.getElementById('responseArea').innerText = JSON.stringify(responseJson, null, 2);
        };
        reader.readAsDataURL(file); // Read the file as a Data URL
    } else {
        alert('Please select a file first!');
    }
};
