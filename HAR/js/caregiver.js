// DOM Elements
const patientSelector = document.querySelector('.patient-selector select');
const emergencyBtn = document.querySelector('.btn-emergency');
const notesForm = document.querySelector('.notes-form');
const notesList = document.querySelector('.notes-list');
const patientList = document.querySelector('.patient-list ul');

// Mock data for demonstration
const mockPatients = [
    { id: 1, name: 'John Doe', status: 'online', lastActivity: 'Walking' },
    { id: 2, name: 'Jane Smith', status: 'offline', lastActivity: 'Sleeping' },
    { id: 3, name: 'Mike Johnson', status: 'online', lastActivity: 'Sitting' }
];

const mockNotes = [
    { id: 1, text: 'Patient had a good day, completed all exercises.', timestamp: '2024-02-20 14:30' },
    { id: 2, text: 'Noticed slight fatigue during evening walk.', timestamp: '2024-02-20 18:15' }
];

// Initialize patient selector
function initializePatientSelector() {
    mockPatients.forEach(patient => {
        const option = document.createElement('option');
        option.value = patient.id;
        option.textContent = patient.name;
        patientSelector.appendChild(option);
    });
}

// Handle patient selection
patientSelector.addEventListener('change', (e) => {
    const selectedPatient = mockPatients.find(p => p.id === parseInt(e.target.value));
    if (selectedPatient) {
        updatePatientStatus(selectedPatient);
        loadPatientNotes(selectedPatient.id);
    }
});

// Update patient status display
function updatePatientStatus(patient) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    const lastActivity = document.querySelector('.last-activity');
    
    statusIndicator.innerHTML = `
        <i class="fas fa-circle ${patient.status === 'online' ? 'text-success' : 'text-muted'}"></i>
        <span>${patient.status === 'online' ? 'Active' : 'Inactive'}</span>
    `;
    
    statusText.textContent = patient.status === 'online' ? 'Patient is active' : 'Patient is inactive';
    lastActivity.textContent = `Last Activity: ${patient.lastActivity}`;
}

// Handle emergency button click
emergencyBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to send an emergency alert? This will notify healthcare providers immediately.')) {
        // In a real application, this would send an API call to notify healthcare providers
        alert('Emergency alert sent! Healthcare providers have been notified.');
    }
});

// Handle notes form submission
notesForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const textarea = notesForm.querySelector('textarea');
    const noteText = textarea.value.trim();
    
    if (noteText) {
        const newNote = {
            id: Date.now(),
            text: noteText,
            timestamp: new Date().toLocaleString()
        };
        
        addNoteToList(newNote);
        textarea.value = '';
    }
});

// Add note to the list
function addNoteToList(note) {
    const noteElement = document.createElement('div');
    noteElement.className = 'note-item';
    noteElement.innerHTML = `
        <div class="note-header">
            <span class="note-time">${note.timestamp}</span>
            <button class="btn-edit" onclick="editNote(${note.id})">
                <i class="fas fa-edit"></i>
            </button>
        </div>
        <p>${note.text}</p>
    `;
    
    notesList.insertBefore(noteElement, notesList.firstChild);
}

// Load patient notes
function loadPatientNotes(patientId) {
    // Clear existing notes
    notesList.innerHTML = '';
    
    // Filter and display notes for the selected patient
    const patientNotes = mockNotes.filter(note => note.patientId === patientId);
    patientNotes.forEach(note => addNoteToList(note));
}

// Edit note
function editNote(noteId) {
    const noteElement = document.querySelector(`[data-note-id="${noteId}"]`);
    const noteText = noteElement.querySelector('p').textContent;
    
    const textarea = notesForm.querySelector('textarea');
    textarea.value = noteText;
    textarea.focus();
    
    // Remove the old note
    noteElement.remove();
}

// Handle patient list item clicks
patientList.addEventListener('click', (e) => {
    const patientItem = e.target.closest('li');
    if (patientItem) {
        // Remove active class from all items
        patientList.querySelectorAll('li').forEach(item => item.classList.remove('active'));
        // Add active class to clicked item
        patientItem.classList.add('active');
        
        // Update patient selector
        const patientId = parseInt(patientItem.dataset.patientId);
        patientSelector.value = patientId;
        
        // Update patient status
        const selectedPatient = mockPatients.find(p => p.id === patientId);
        if (selectedPatient) {
            updatePatientStatus(selectedPatient);
            loadPatientNotes(patientId);
        }
    }
});

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    initializePatientSelector();
    
    // Set initial patient
    const initialPatient = mockPatients[0];
    if (initialPatient) {
        patientSelector.value = initialPatient.id;
        updatePatientStatus(initialPatient);
        loadPatientNotes(initialPatient.id);
    }
}); 