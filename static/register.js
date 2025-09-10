document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector("#registerForm");

    registerForm.addEventListener("submit", e => {
        e.preventDefault(); // Stop form from submitting

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (username === "" || password === "") {
            alert("Please provide both a username and a password.");
            return;
        }

        // --- email validation, (could be nice for the future maybe) ---
        /*
        const email = document.getElementById("Email").value;
        const nemail = email.length;
        const iemail = email.includes("@gmail.com");

        if (nemail === 0 || !iemail) {
            alert("Please enter a valid email address.");
            return;
        }
        */

        // If validation passes
        alert("Registration successful!");
        // You can redirect to the login page after successful registration
        // window.location.href = "login.html";
    });
});