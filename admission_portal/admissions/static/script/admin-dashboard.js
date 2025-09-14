document.addEventListener('DOMContentLoaded', function () {
  // ==========================
  // Enrollment Trends
  // ==========================
  new Chart(document.getElementById('enrollmentTrendChart').getContext('2d'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
      datasets: [{
        label: 'Enrollments',
        data: [30, 45, 60, 40, 70, 90, 100],
        borderColor: '#1e40af',
        backgroundColor: 'rgba(0, 33, 71, 0.2)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });

  // ==========================
  // Academic Year Distribution
  // ==========================
  new Chart(document.getElementById('yearChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['2024-2025', '2025-2026', '2026-2027'],
      datasets: [{
        label: 'No. of Students',
        data: [200, 250, 180],
        backgroundColor: '#1e40af'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });

  // ==========================
// Program Popularity (Pie Chart)
// ==========================
new Chart(document.getElementById('programChart').getContext('2d'), {
  type: 'pie',
  data: {
    labels: ['BSCS', 'BSIT', 'BSCE', 'BSBA'],
    datasets: [{
      data: [80, 70, 60, 40],
      backgroundColor: ['#1e40af', '#FFD700', '#059669', '#0891b2']
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right', // move legend to the side for clarity
        labels: {
          font: {
            size: 14
          }
        }
      }
    }
  }
});

  // ==========================
  // Admission Success Rate
  // ==========================
  new Chart(document.getElementById('admissionChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Approved', 'Pending', 'Rejected'],
      datasets: [{
        label: 'Applicants',
        data: [300, 100, 50],
        backgroundColor: ['#1e40af', '#059669', '#dc2626']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
});


  // Chart toggle buttons
  document.querySelectorAll('.chart-btn').forEach((btn) => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.chart-btn').forEach((b) =>
        b.classList.remove('active')
      );
      this.classList.add('active');

      programChart.destroy();
      programChartType = this.dataset.chart;
      programChart = new Chart(programCtx, {
        type: programChartType,
        data: {
          labels: ['BSCS', 'BSIT', 'BSCE', 'BSBA'],
          datasets: [
            {
              data: [80, 70, 60, 40],
              backgroundColor: ['#1e40af', '#059669', '#FFD700', '#0891b2'],
            },
          ],
        },
        options:
          programChartType === 'bar'
            ? { scales: { y: { beginAtZero: true } } }
            : {},
      });
    });
  });

  // ==========================
  // Gender Distribution
  // ==========================
  new Chart(document.getElementById('genderChart').getContext('2d'), {
    type: 'pie',
    data: {
      labels: ['Male', 'Female'],
      datasets: [
        {
          data: [220, 230],
          backgroundColor: ['#1e40af', '#FFD700'],
        },
      ],
    },
  });

  // ==========================
  // Admission Success Rate
  // ==========================
  new Chart(document.getElementById('admissionChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Approved', 'Pending', 'Rejected'],
      datasets: [
        {
          label: 'Applicants',
          data: [300, 100, 50],
          backgroundColor: ['#059669', '#FFD700', '#dc2626'],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
    },
  });


// ==========================
// Section Tab Switching
// ==========================
function showSection(id) {
  document.querySelectorAll('.section-content').forEach(sec => {
    sec.classList.remove('active');
  });
  document.getElementById(id).classList.add('active');

  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelector(`.tab-btn[onclick="showSection('${id}')"]`).classList.add('active');
}
window.showSection = showSection;

// ==========================
// Logout (placeholder)
// ==========================
function logout() {
  window.location.href = "/";
}
window.logout = logout;
// ==========================
// Search & Reset
// ==========================
document.getElementById('searchBtn').addEventListener('click', function () {
  const nameSearch = document.getElementById('nameSearch').value.toLowerCase();
  const programFilter = document.getElementById('programFilter').value;
  const chanceSearch = document.getElementById('chanceSearch').value;

  let found = false;
  document.querySelectorAll('#studentTable tbody tr').forEach(row => {
    const name = row.cells[2].innerText.toLowerCase();
    const program = row.cells[3].innerText;
    const chance = row.cells[5].innerText;

    let match = true;
    if (nameSearch && !name.includes(nameSearch)) match = false;
    if (programFilter && !program.includes(programFilter)) match = false;
    if (chanceSearch && !chance.includes(chanceSearch)) match = false;

    row.style.display = match ? '' : 'none';
    if (match) found = true;
  });

  document.getElementById('noResults').style.display = found ? 'none' : 'block';
});

document.getElementById('resetBtn').addEventListener('click', function () {
  document.getElementById('nameSearch').value = '';
  document.getElementById('programFilter').value = '';
  document.getElementById('chanceSearch').value = '';
  
  document.querySelectorAll('#studentTable tbody tr').forEach(row => row.style.display = '');
  document.getElementById('noResults').style.display = 'none';
});

// ==========================
// Select All Checkboxes
// ==========================
document.getElementById('selectAll').addEventListener('change', function () {
  const checked = this.checked;
  document.querySelectorAll('.row-select').forEach(cb => cb.checked = checked);
});

