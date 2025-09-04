document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#domain-form');
    const spinner = document.querySelector('#spinner');
    const answerDiv = document.querySelector('#answer');
    const closeButton = document.querySelector('#close-answer');
    const domainInput = document.querySelector('#domain-input');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const domain = domainInput.value.trim().toLowerCase();
        // added validation for 'top domains'
        // list of allowed domain
        const allowedTLDs = [".com", ".org", ".net", ".edu"];
        //check if domain ends with one of them
        const isValid = allowedTLDs.some(tld => domain.endsWith(tld));

        if (!isValid) {
            alert("invalid url format. please enter a valid domain (e.g. example.com)");
            domainInput.value = ""; // means clear input
            domainInput.focus();  // focus back to input
            return;

        }
        
        
        if (domain) {
            getDomainInfo(domain);
        }
    });

    closeButton.addEventListener('click', function() {
        answerDiv.style.display = 'none';
    });

    async function getDomainInfo(domain) {
        spinner.style.display = 'block';
        answerDiv.style.display = 'none';

        try {
            const response = await fetch(`/check_domain?domain=${domain}`);
            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Error fetching domain data:', error);
            alert('Failed to retrieve domain information. Please check the console for details.');
        } finally {
            spinner.style.display = 'none';
        }
    }

    function displayResults(data) {
        document.querySelector('#domain-name').textContent = data.domain;
        document.querySelector('#status-code').textContent = data.status_code;
        document.querySelector('#cert-status').textContent = data.certificate_status;
        document.querySelector('#issuer').textContent = data.issuer;
        document.querySelector('#cert-expiry').textContent = data.certificate_expiry;
        
        const healthStatusEl = document.querySelector('#health-status');
        if (data.healthy) {
            healthStatusEl.innerHTML = 'Healthy &#x1F44D;'; // Thumbs Up
            healthStatusEl.style.color = 'green';
        } else {
            healthStatusEl.innerHTML = 'Not Healthy &#x1F44E;'; // Thumbs Down
            healthStatusEl.style.color = 'red';
        }

        answerDiv.style.display = 'block';
    }
});
