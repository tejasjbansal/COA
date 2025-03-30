// script.js
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const resultsSection = document.getElementById('results-section');
    const loadingIndicator = document.getElementById('loading-indicator');
    const downloadPdfBtn = document.getElementById('download-pdf');
    
    // File preview handling
    document.getElementById('supplier-coa').addEventListener('change', function(e) {
        updateFilePreview(e.target, 'supplier-preview');
    });
    
    document.getElementById('manufacturer-results').addEventListener('change', function(e) {
        updateFilePreview(e.target, 'manufacturer-preview');
    });
    
    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading indicator
        resultsSection.style.display = 'block';
        document.getElementById('results-content').style.display = 'none';
        loadingIndicator.style.display = 'block';
        
        // Get form data
        const formData = new FormData(uploadForm);
        
        // Send to backend
        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            document.getElementById('results-content').style.display = 'block';
            
            // Populate results
            populateResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            alert('An error occurred while processing your documents. Please try again.');
        });
    });
    
    // Download PDF functionality
    downloadPdfBtn.addEventListener('click', function() {
        generatePDF();
    });
    
    // Functions
    function updateFilePreview(input, previewId) {
        const preview = document.getElementById(previewId);
        if (input.files && input.files[0]) {
            const fileName = input.files[0].name;
            preview.innerHTML = `<p>${fileName}</p>`;
        } else {
            preview.innerHTML = '<p>No file selected</p>';
        }
    }
    
    function populateResults(data) {
        // Set batch info
        document.getElementById('result-batch-ref').textContent = data.batch_info.batch_reference;
        document.getElementById('result-supplier-batch').textContent = data.batch_info.supplier_batch;
        document.getElementById('result-product').textContent = data.batch_info.product;
        document.getElementById('result-date').textContent = data.batch_info.comparison_date;
        
        // Populate tables
        populateTable('physical-table', data.physical_characteristics);
        populateTable('chemical-table', data.chemical_analysis);
        populateTable('micro-table', data.microbiological_testing);
        
        // Set compliance summary
        const overallCompliance = document.getElementById('overall-compliance');
        overallCompliance.textContent = data.compliance_summary.overall_compliance;
        if (data.compliance_summary.overall_compliance === 'FULLY COMPLIANT') {
            overallCompliance.classList.add('compliant');
        } else {
            overallCompliance.classList.add('non-compliant');
        }
        
        document.getElementById('variation-tolerance').textContent = data.compliance_summary.variation_tolerance;
        
        const batchApproval = document.getElementById('batch-approval');
        batchApproval.textContent = data.compliance_summary.batch_approval_status;
        if (data.compliance_summary.batch_approval_status === 'APPROVED') {
            batchApproval.classList.add('approved');
        } else {
            batchApproval.classList.add('rejected');
        }
        
        // Set certification
        document.getElementById('certified-by').textContent = data.certification.certified_by;
        document.getElementById('reviewed-by').textContent = data.certification.reviewed_by;
        document.getElementById('certification-number').textContent = data.certification.certification_number;
        document.getElementById('certification-date').textContent = data.certification.certification_date;
    }
    
    function populateTable(tableId, data) {
        const tableBody = document.getElementById(tableId).querySelector('tbody');
        tableBody.innerHTML = '';
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            // Create cells
            const paramCell = document.createElement('td');
            paramCell.textContent = item.parameter || item.test;
            
            const supplierCell = document.createElement('td');
            supplierCell.textContent = item.supplier_result;
            
            const manufacturerCell = document.createElement('td');
            manufacturerCell.textContent = item.manufacturer_result;
            
            const statusCell = document.createElement('td');
            statusCell.textContent = item.status;
            
            if (item.status === 'MATCH') {
                statusCell.className = 'status-match';
            } else if (item.status === 'WITHIN TOLERANCE' || item.status === 'COMPLIANT') {
                statusCell.className = 'status-compliant';
            } else {
                statusCell.className = 'status-fail';
            }
            
            // Append cells to row
            row.appendChild(paramCell);
            row.appendChild(supplierCell);
            row.appendChild(manufacturerCell);
            row.appendChild(statusCell);
            
            // Append row to table body
            tableBody.appendChild(row);
        });
    }
    
    function generatePDF() {
        // Get current date
        const today = new Date();
        const dateString = today.toISOString().split('T')[0];
        
        // Get batch reference
        const batchRef = document.getElementById('result-batch-ref').textContent;
        
        // Create filename
        const filename = `Compliance_Report_${batchRef}_${dateString}.pdf`;
        
        // Get the element to convert
        const element = document.getElementById('results-content');
        
        // Set up jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        
        // Add header
        doc.setFontSize(18);
        doc.setTextColor(44, 123, 229);
        doc.text('LifeScience Pharmaceuticals', 105, 20, { align: 'center' });
        doc.setFontSize(14);
        doc.text('Comparative Compliance Certificate', 105, 30, { align: 'center' });
        
        // Use html2canvas to capture the content
        html2canvas(element, {
            scale: 2,
            useCORS: true,
            logging: false,
            width: element.scrollWidth,
            height: element.scrollHeight
        }).then(canvas => {
            // Convert the canvas to an image
            const imgData = canvas.toDataURL('image/png');
            
            // Calculate the PDF dimensions
            const imgProps = doc.getImageProperties(imgData);
            const pdfWidth = doc.internal.pageSize.getWidth() - 20;
            const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
            
            // Add the image to the PDF
            doc.addImage(imgData, 'PNG', 10, 40, pdfWidth, pdfHeight);
            
            // Save the PDF
            doc.save(filename);
        });
    }
});