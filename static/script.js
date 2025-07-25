document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('spam-form');
    const messageInput = document.getElementById('message');
    const submitButton = document.getElementById('submit-button');
    const buttonText = document.getElementById('button-text');
    const spinner = document.getElementById('spinner');
    const resultContainer = document.getElementById('result-container');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;
        setLoading(true);
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            if (!response.ok) throw new Error(`Server error: ${response.status}`);
            const data = await response.json();
            displayResult(data);
        } catch (error) {
            console.error('Error:', error);
            displayError('Could not connect to the server. Please try again.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitButton.disabled = true;
            buttonText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            submitButton.disabled = false;
            buttonText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }

    function displayResult(data) {
        const isSpam = data.prediction === 'SPAM';
        const cardBg = isSpam ? 'bg-red-100 border-red-400' : 'bg-green-100 border-green-400';
        const iconBg = isSpam ? 'bg-red-200' : 'bg-green-200';
        const iconColor = isSpam ? 'text-red-600' : 'text-green-600';
        const textColor = isSpam ? 'text-red-800' : 'text-green-800';
        const iconSvg = isSpam
            ? `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ${iconColor}" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>`
            : `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ${iconColor}" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;

        const resultHtml = `
            <div id="result-card" class="rounded-lg p-5 border-l-4 ${cardBg}">
                <div class="flex items-center">
                    <div class="flex-shrink-0 w-12 h-12 rounded-full ${iconBg} flex items-center justify-center">
                        ${iconSvg}
                    </div>
                    <div class="ml-4">
                        <p class="font-bold text-xl ${textColor}">This message is ${data.prediction}</p>
                        <p class="text-sm ${textColor.replace('800', '600')}">Confidence: ${data.confidence}%</p>
                    </div>
                </div>
            </div>
        `;
        resultContainer.innerHTML = resultHtml;
        setTimeout(() => {
            document.getElementById('result-card').classList.add('visible');
        }, 10);
    }

    function displayError(message) {
        const errorHtml = `
            <div id="result-card" class="rounded-lg p-5 border-l-4 bg-yellow-100 border-yellow-400 visible">
                <p class="font-semibold text-yellow-800">${message}</p>
            </div>
        `;
        resultContainer.innerHTML = errorHtml;
    }
});
