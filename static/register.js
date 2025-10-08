// MODIFICATION: The entire file is updated to use the Fetch API.
document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector("#registerForm");
    const messageDiv = document.querySelector("#formMessage");

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // Stop form from submitting

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (username === "" || password === "") {
            messageDiv.textContent = "Please provide both a username and a password.";
            messageDiv.className = "form__message form__message--error";
            return;
        }

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // On success, show message and redirect to login page.
                messageDiv.textContent = data.message;
                messageDiv.className = "form__message form__message--success";
                setTimeout(() => {
                    window.location.href = "/login";
                }, 2000); // Wait 2 seconds before redirecting
            } else {
                // Display error message from the API.
                messageDiv.textContent = data.message || "An unknown error occurred.";
                messageDiv.className = "form__message form__message--error";
            }
        } catch (error) {
            console.error("Registration failed:", error);
            messageDiv.textContent = "Could not connect to the server. Please try again later.";
            messageDiv.className = "form__message form__message--error";
        }
    });
});