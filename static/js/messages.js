// Function to hide messages after 3 seconds
setTimeout(() => {
    const messages = document.querySelectorAll('.messages li');
    messages.forEach(message => {
        message.style.display = 'none';
    });
}, 3000);