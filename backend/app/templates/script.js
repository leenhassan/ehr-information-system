document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const tableBody = document.querySelector("tbody");

    // Handle the form submission
    form.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent page refresh

        // Get input values
        const name = document.getElementById("patient-name").value;
        const age = document.getElementById("patient-age").value;
        const condition = document.getElementById("patient-condition").value;

        // Create a new row for the table
        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td>${name}</td>
            <td>${age}</td>
            <td>${condition}</td>
            <td>
                <button class="btn btn-success btn-sm">Edit</button>
                <button class="btn btn-danger btn-sm">Delete</button>
            </td>
        `;

        // Add the new row to the table
        tableBody.appendChild(newRow);

        // Clear the form inputs
        form.reset();
    });

    // Handle the click event on table (for delete and edit)
    tableBody.addEventListener("click", (event) => {
        if (event.target.classList.contains("btn-danger")) {
            // Find the row to delete
            const rowToDelete = event.target.closest("tr");
            rowToDelete.remove(); // Remove the row
        }

        if (event.target.classList.contains("btn-success")) {
            // Get the current row
            const rowToEdit = event.target.closest("tr");

            // Extract current values from the row
            const nameCell = rowToEdit.children[0];
            const ageCell = rowToEdit.children[1];
            const conditionCell = rowToEdit.children[2];

            // Prompt the user for new values
            const newName = prompt("Edit Patient Name:", nameCell.textContent);
            const newAge = prompt("Edit Age:", ageCell.textContent);
            const newCondition = prompt("Edit Condition:", conditionCell.textContent);

            // Update the row with new values
            if (newName !== null) nameCell.textContent = newName;
            if (newAge !== null) ageCell.textContent = newAge;
            if (newCondition !== null) conditionCell.textContent = newCondition;
        }
    });
    

    // ICD-10 Converter Data
    const icdData = {
        "A00": "Cholera",
        "B20": "HIV Disease",
        "C34": "Malignant neoplasm of bronchus and lung",
        "D50": "Iron deficiency anemia",
        "E11": "Type 2 diabetes mellitus"
    };

    // ICD-10 Converter Functionality
    const icdForm = document.getElementById("icd-form");
    const icdResult = document.getElementById("icd-result");

    icdForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent form submission

        const icdCode = document.getElementById("icd-code").value.trim().toUpperCase();
        const description = icdData[icdCode];

        // Display the result
        if (description) {
            icdResult.innerHTML = `<p><strong>ICD Code:</strong> ${icdCode}</p>
                                   <p><strong>Description:</strong> ${description}</p>`;
        } else {
            icdResult.innerHTML = `<p style="color: red;">ICD Code not found. Please try again.</p>`;
        }
    });

    // Validate Password Strength
    const passwordInput = document.getElementById("password");
    const passwordStrengthText = document.getElementById("password-strength");

    passwordInput.addEventListener("input", () => {
        const password = passwordInput.value;
        if (password.length < 8) {
            passwordStrengthText.textContent = "Password must be at least 8 characters.";
            passwordStrengthText.style.color = "red";
        } else if (!/\d/.test(password)) {
            passwordStrengthText.textContent = "Password must contain at least one number.";
            passwordStrengthText.style.color = "red";
        } else if (!/[!@#$%^&*]/.test(password)) {
            passwordStrengthText.textContent = "Password must contain at least one symbol (!@#$%^&*).";
            passwordStrengthText.style.color = "red";
        } else {
            passwordStrengthText.textContent = "Strong password!";
            passwordStrengthText.style.color = "green";
        }
    });

    // Validate Doctor ID
    const registrationForm = document.getElementById("registration-form");

    registrationForm.addEventListener("submit", (event) => {
        const doctorId = document.getElementById("doctor-id").value;
        if (!doctorId.endsWith("403")) {
            event.preventDefault(); // Stop form submission
            alert("Doctor ID must end with '403' to verify your department.");
        }
    });

    // Handle login form submission
    const loginForm = document.getElementById("login-form");
    const loginFeedback = document.getElementById("login-feedback");

    const registeredDoctors = [
        { email: "doctor1@example.com", password: "Password123!" },
        { email: "doctor2@example.com", password: "StrongPass456@" },
    ];

    loginForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent form submission

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        // Check if the email and password match any registered doctor
        const doctor = registeredDoctors.find(doc => doc.email === email && doc.password === password);

        if (doctor) {
            loginFeedback.textContent = "Login successful! Redirecting to the dashboard...";
            loginFeedback.style.color = "green";

            // Redirect to the dashboard (for now, use a timeout to simulate)
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 2000);
        } else {
            loginFeedback.textContent = "Invalid email or password. Please try again.";
            loginFeedback.style.color = "red";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    function updateDateTime() {
        // Get the current date and time
        const now = new Date();

        // Format the date and time
        const date = now.toLocaleDateString(); // e.g., "01/12/2025"
        const time = now.toLocaleTimeString(); // e.g., "12:34:56 PM"

        // Display the date and time in the element with id "date-time"
        document.getElementById("date-time").textContent = `${date} ${time}`;
    }

    // Update the date and time immediately
    updateDateTime();

    // Update the date and time every second
    setInterval(updateDateTime, 1000); // Update every second
});

function submitForm() {
    // Get values from the form fields
    var name = document.getElementById("patient-name").value;
    var age = document.getElementById("patient-age").value;
    var condition = document.getElementById("patient-condition").value;

    // Get the selected gender value (Male or Female)
    var gender = document.querySelector('input[name="gender"]:checked'); // Get the selected radio button
    if (gender) {
        gender = gender.value;  // Extract the value (Male or Female)
    } else {
        gender = "Not specified"; // If no gender is selected, default to "Not specified"
    }

    // Check if any field is empty
    if (!name || !age || !condition || !gender) {
        alert("Please fill out all fields.");
        return; // Stop the form from submitting if any field is empty
    }

    // Create a new row in the table with the patient's data
    var table = document.querySelector("table tbody");
    var newRow = table.insertRow();  // Insert a new row at the end of the table

    // Insert data into the new row's cells
    var cell1 = newRow.insertCell(0);  // Patient Name
    var cell2 = newRow.insertCell(1);  // Age
    var cell3 = newRow.insertCell(2);  // Condition
    var cell4 = newRow.insertCell(3);  // Gender
    var cell5 = newRow.insertCell(4);  // Actions

    // Assign values to each cell
    cell1.textContent = name;
    cell2.textContent = age;
    cell3.textContent = condition;
    cell4.textContent = gender;

    // Create Edit button
    var editButton = document.createElement("button");
    editButton.className = "btn btn-success btn-sm";
    editButton.textContent = "Edit";
    cell5.appendChild(editButton);

    // Create Delete button
    var deleteButton = document.createElement("button");
    deleteButton.className = "btn btn-danger btn-sm";
    deleteButton.textContent = "Delete";
    cell5.appendChild(deleteButton);

    // Reset the form after adding the patient
    document.querySelector("form").reset();
}

// Optionally, add event listeners to handle button clicks if needed for actions
document.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();  // Prevent default form submission
    submitForm();  // Call the function to submit the form
});


