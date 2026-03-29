// helper funkcija za poziv backend-a
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

const harvestThreadMain = () => {
    chrome.storage.local.get("enabled", (res) => {
        if (res.enabled === false) return;

        const mails = document.querySelectorAll('div[role="listitem"]:not([data-scanned="true"])');

        mails.forEach(async (mail) => {
            mail.setAttribute('data-scanned', 'true');

            const senderElement = mail.querySelector('span.gD');
            const senderEmail = senderElement?.getAttribute('email') || "";
            const subjectElement = mail.querySelector('h2.hP');

            // poziv backend-a
            const result = await checkEmailOnBackend(senderEmail);

            // bojenje na osnovu rezultata
            if (result.includes("skem")) {
                mail.style.borderLeft = "8px solid #ff0000";
                mail.style.backgroundColor = "rgba(255, 0, 0, 0.15)";
            } else if (result.includes("dobar")) {
                mail.style.borderLeft = "8px solid #00ff00";
                mail.style.backgroundColor = "rgba(0, 255, 0, 0.15)";
            } else {
                mail.style.borderLeft = "5px solid #ffdf00";
                mail.style.backgroundColor = "rgba(255, 223, 0, 0.1)";
            }
        });
    });
};

setInterval(harvestThreadMain, 2000);
