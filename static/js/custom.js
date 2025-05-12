/**
 * Camp de Vacances - Utility functions
 */

// Show/hide notifications
function toggleNotification(id, show = true) {
    const notification = document.getElementById(id);
    if (notification) {
        if (show) {
            notification.classList.remove('hidden');
            setTimeout(() => {
                notification.classList.add('hidden');
            }, 5000); // Auto-hide after 5 seconds
        } else {
            notification.classList.add('hidden');
        }
    }
}

// Format date to locale string
function formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', options);
}

// Format time to locale string
function formatTime(dateString, options = {}) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('fr-FR', options);
}

// Calculate age from birthdate
function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

// Format currency
function formatCurrency(amount, locale = 'fr-FR', currency = 'EUR') {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Confirm action with modal
function confirmAction(message, actionCallback) {
    if (confirm(message)) {
        actionCallback();
    }
}

// AJAX helper
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}

// Debounce function for search inputs
function debounce(func, wait = 300) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Initialize search with debounce
function initSearch(inputId, formId) {
    const searchInput = document.getElementById(inputId);
    const searchForm = document.getElementById(formId);
    
    if (searchInput && searchForm) {
        searchInput.addEventListener('input', debounce(() => {
            searchForm.submit();
        }, 500));
    }
}

// Prints a specific element
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Impression</title>
                    <link rel="stylesheet" href="/static/css/tailwind.css" />
                    <style>@media print { body { font-size: 12pt; } }</style>
                </head>
                <body>
                    ${element.innerHTML}
                    <script>window.onload = function() { window.print(); window.close(); }</script>
                </body>
            </html>
        `);
        printWindow.document.close();
    }
}

// Generate a PDF from element
function generatePDF(elementId, filename = 'document.pdf') {
    // This is a placeholder - in a real app you would use a library like jsPDF
    alert('Fonctionnalité de génération PDF en développement');
}

// Export data to CSV
function exportToCSV(data, filename = 'export.csv') {
    if (!data || !data.length) {
        console.error('No data to export');
        return;
    }
    
    // Get headers
    const headers = Object.keys(data[0]);
    
    // Create CSV content
    let csvContent = headers.join(',') + '\n';
    
    data.forEach(item => {
        const row = headers.map(header => {
            // Escape commas and quotes
            const value = item[header] !== null && item[header] !== undefined ? item[header].toString() : '';
            return `"${value.replace(/"/g, '""')}"`;
        });
        csvContent += row.join(',') + '\n';
    });
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Helper function to check activity capacity via AJAX
async function checkActivityCapacity(activityId, updateElementId) {
    const updateElement = document.getElementById(updateElementId);
    if (!updateElement) return;
    
    try {
        const data = await fetchData(`/activities/check-capacity/${activityId}/`);
        if (data && data.success) {
            if (data.is_full) {
                updateElement.innerHTML = `<span class="badge badge-red">Complet (${data.current_participants}/${data.total_capacity})</span>`;
            } else {
                updateElement.innerHTML = `<span class="badge badge-green">Places disponibles: ${data.available_spots}</span>`;
            }
        }
    } catch (error) {
        console.error('Error checking capacity:', error);
    }
}