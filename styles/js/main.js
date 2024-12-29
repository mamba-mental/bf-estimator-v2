// styles/js/main.js

document.addEventListener('DOMContentLoaded', (event) => {
    const fillLastReportDataBtn = document.getElementById('fillLastReportDataBtn');

    if (fillLastReportDataBtn) {
        fillLastReportDataBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fillLastReportData();
        });
    }
});

function fillLastReportData() {
    document.getElementById('loading-spinner').style.display = 'block';
    fetch('/get_last_report_data')
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Unknown error');
                });
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('loading-spinner').style.display = 'none';
            if (data.error) {
                alert(data.error);
                return;
            }
            fillForm(data);
            console.log("Form filled with last report data");
        })
        .catch(error => {
            document.getElementById('loading-spinner').style.display = 'none';
            console.error('Error fetching last report data:', error);
            alert("Failed to fetch last report data. Please try again.");
        });
}

function fillForm(data) {
    // Helper function to find and fill form fields
    function fillField(name, value) {
        // Try to find the field in the main form first
        let element = document.querySelector(`form[action="/"] [name="${name}"]`);
        
        // If not found in main form, try weekly update form
        if (!element) {
            element = document.querySelector(`form[action="/update_weekly"] [name="${name}"]`);
        }
        
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = value === 'y' || value === true;
            } else if (element.tagName === 'SELECT') {
                const option = Array.from(element.options).find(option => 
                    option.value === (value || '').toString());
                if (option) {
                    option.selected = true;
                } else {
                    console.warn(`No matching option found for ${name} with value ${value}`);
                }
            } else {
                element.value = value || '';
            }
            console.log(`Set ${name} to ${value}`);
        } else {
            console.warn(`Form field not found: ${name}`);
        }
    }

    // Fill each field
    Object.entries(data).forEach(([key, value]) => fillField(key, value));

    // Special handling for weekly update form
    const weeklyWeight = document.querySelector('form[action="/update_weekly"] [name="weekly_weight"]');
    const weeklyBf = document.querySelector('form[action="/update_weekly"] [name="weekly_bf"]');
    if (weeklyWeight) weeklyWeight.value = data.current_weight || '';
    if (weeklyBf) weeklyBf.value = data.current_bf || '';
}
