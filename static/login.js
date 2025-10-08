// MODIFICATION: The entire file is updated to use the Fetch API.
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("#loginForm");
    const messageDiv = document.querySelector("#formMessage");

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent the default form submission.

        // Get values from the form
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (username === "" || password === "") {
            messageDiv.textContent = "Please fill in both username and password.";
            messageDiv.className = "form__message form__message--error";
            return;
        }

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // On successful login, redirect to the dashboard.
                messageDiv.textContent = data.message;
                messageDiv.className = "form__message form__message--success";
                window.location.href = "/dashboard";
            } else {
                // Display error message from the API.
                messageDiv.textContent = data.message || "An unknown error occurred.";
                messageDiv.className = "form__message form__message--error";
            }
        } catch (error) {
            console.error("Login failed:", error);
            messageDiv.textContent = "Could not connect to the server. Please try again later.";
            messageDiv.className = "form__message form__message--error";
        }
    });
});