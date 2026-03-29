/// helper funkcija za poziv backend-a
async function checkEmailOnBackend(email) {
    try {
        const response = await fetch("http://localhost:8000/mail/check-one-mail", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });
        const data = await response.json();
        return data.result;
    } catch (err) {
        console.error("Error checking email:", err);
        return "unknown";
    }
}

const harvestListMain = () => {
    chrome.storage.local.get("enabled", (res) => {
        if (res.enabled === false) return;

        const rows = document.querySelectorAll('tr[role="row"]:not([data-scanned])');

        rows.forEach(async (row) => {
            row.setAttribute('data-scanned', 'true');

            const senderElement = row.querySelector('.zF, [email]');
            const senderEmail = senderElement?.getAttribute('email') || "";
            const subjectElement = row.querySelector('.bog');
            
            // poziv backend-a
            const result = await checkEmailOnBackend(senderEmail);

            // bojenje na osnovu rezultata
            if (result.includes("skem")) {
                row.style.borderLeft = "8px solid #ff0000";
                row.style.backgroundColor = "rgba(255, 0, 0, 0.15)";
            } else if (result.includes("dobar")) {
                row.style.borderLeft = "8px solid #00ff00";
                row.style.backgroundColor = "rgba(0, 255, 0, 0.15)";
            } else {
                row.style.borderLeft = "5px solid #ffdf00";
                row.style.backgroundColor = "rgba(255, 223, 0, 0.1)";
            }
        });
    });
};

setInterval(harvestListMain, 2000);
