document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("#loginForm");

    loginForm.addEventListener("submit", e => {
        e.preventDefault(); // Prevent the form from submitting normally

        // Get values from the form
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Basic validation
        if (username === "" || password === "") {
            alert("Please fill in both username and password.");
            return;
        }

        // Placeholder for actual login logic
        if (username === "admin" && password === "admin") {
            alert("Login successful!");
            // Here you would typically redirect the user
            // window.location.href = "/dashboard";
        } else {
            alert("Invalid username or password.");
        }
    });
});